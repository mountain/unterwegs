import os
import time
import uuid
import json

import unterwegs.tasks.uploader as upldr

from flask import Response, request, render_template, send_from_directory, url_for, redirect
from uuid import uuid5
from .app import create_app
from unterwegs.utils.db import wd, rd, ts, rn
from unterwegs.utils.pages import search_result, coocurrence_nodes, coocurrence_links, frequency_of, recommend


specs = {}
application = create_app()

root_dir = os.path.dirname(os.getcwd())


def load_spec():
    from os.path import basename
    from glob import glob
    for pth in glob('/web/unterwegs/spec/*.json'):
        key = basename(pth)[:-5]
        with open(pth) as j:
            specs[key] = json.load(j)


load_spec()


@application.route('/article')
def article():
    return redirect(url_for('article_by', id=request.args['id']))


@application.route('/page')
def page():
    return redirect(url_for('page_by', id=request.args['id']))


@application.route('/search')
def search():
    return redirect(url_for('search_by', q=request.args['q']))


@application.route('/article/<string:aid>')
def article_by(aid):
    pids = [pid.decode('utf-8') for pid in rd.zrange('article:%s' % aid, 0, -1)]
    return render_template('article.html',
        aid=aid,
        pids=pids,
    )


@application.route('/page/<string:pid>')
def page_by(pid):
    pid2aid = {}
    aid = rd.get('articleOf:page:%s' % pid).decode('utf-8')
    rlist = recommend(pid)
    for p in rlist:
        pid2aid[p] = rd.get('articleOf:page:%s' % p).decode('utf-8')

    return render_template('page.html',
        pid=pid,
        aid=aid,
        rlist=rlist,
        pid2aid=pid2aid,
    )


@application.route('/search/<string:q>')
def search_by(q):
    rs = search_result(q=q)
    return render_template('search.html',
        query=q, results=rs,
        specPage=url_for('get_spec', q=q, pid='_', specname='page', _external=True),
        specAnalysis=url_for('get_spec', q=q, pid='_', specname='analysis', _external=True),
        specCluster=url_for('get_spec', q=q, pid='_', specname='cluster', _external=True)
    )


@application.route('/spec/<string:q>/<string:pid>/<string:specname>.json')
def get_spec(q, pid, specname):
    spec = specs[specname]
    if specname == 'cluster':
        spec['data'][0]['url'] = url_for('get_data', q=q, pid=pid, dataname='nodes', _external=True)
        spec['data'][1]['url'] = url_for('get_data', q=q, pid=pid, dataname='links', _external=True)
    if specname == 'analysis':
        spec['data'][0]['url'] = url_for('get_data', q=q, pid=pid, dataname='frequency', _external=True)

    return Response(json.dumps(spec), content_type='application/json')


@application.route('/data/<string:q>/<string:pid>/<string:dataname>.json')
def get_data(q, pid, dataname):
    data = []
    result = search_result(q)
    if dataname == 'nodes':
        data = coocurrence_nodes(q, result['hits'])
    elif dataname == 'links':
        data = coocurrence_links(q, result['hits'])
    elif dataname == 'frequency':
        data = frequency_of(q, pid, result['hits'])

    return Response(json.dumps(data), content_type='application/json')


@application.route('/page/<string:pid>.png')
def get_page_png(pid):
    return Response(wd.get_file(rd.get('png:%s' % pid).decode('utf-8')), content_type='image/png')


@application.route('/page/<string:pid>.pdf')
def get_page_pdf(pid):
    return Response(wd.get_file(pid), content_type='application/pdf')


@application.route("/upload", methods=["POST"])
def upload():
    upload_key = uuid5(uuid.NAMESPACE_URL, str(time.time())).hex
    target = "/uploads/{}".format(upload_key)
    for upload in request.files.getlist("upload"):
        filename = upload.filename.rsplit("/")[0]
        destination = "-".join([target, filename])
        upload.save(destination)
        upldr.fire.delay(destination)

    return 'OK'


@application.route("/style/<path:filename>", methods=["GET"])
def style(filename):
    return send_from_directory(os.path.join(root_dir, 'public', 'style'), filename, cache_timeout=0)


@application.route("/js/<path:filename>", methods=["GET"])
def js(filename):
    return send_from_directory(os.path.join(root_dir, 'public', 'js'), filename, cache_timeout=0)


@application.route("/vega/<path:filename>", methods=["GET"])
def vega(filename):
    return send_from_directory(os.path.join(root_dir, 'public', 'vega'), filename)
