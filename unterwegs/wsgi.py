import os
import time
import uuid
import json

import unterwegs.tasks.uploader as upldr

from flask import request, render_template, send_from_directory, url_for, Response
from uuid import uuid5
from .app import create_app
from unterwegs.utils.db import wd, rd, ts
from unterwegs.utils.pages import coocurrence


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


@application.route('/search/<string:q>')
def search(q):
    return render_template('vega.html',
        query=q,
        specPage=url_for('get_spec', q=q, specname='page', _external=True),
        specInfo=url_for('get_spec', q=q, specname='info', _external=True),
        specAnalysis=url_for('get_spec', q=q, specname='analysis', _external=True),
        specCluster=url_for('get_spec', q=q, specname='cluster', _external=True)
    )


@application.route('/spec/<string:q>/<string:specname>.json')
def get_spec(q, specname):
    spec = specs[specname]
    if specname == 'cluster':
        spec['data'][0]['url'] = url_for('get_data', q=q, dataname='nodes', _external=True)
        spec['data'][1]['url'] = url_for('get_data', q=q, dataname='links', _external=True)

    return Response(json.dumps(spec), content_type='application/json')


@application.route('/data/<string:q>/<string:dataname>.json')
def get_data(q, dataname):
    data = []
    if dataname == 'nodes':
        result = ts.collections['pages'].documents.search({
            'q': q,
            'per_page': 200,
            'query_by': 'content',
            'sort_by': '_text_match:desc',
            'include_fields': 'id'
        })

        nodes, links = coocurrence(result['hits'])
        data = nodes
    elif dataname == 'links':
        result = ts.collections['pages'].documents.search({
            'q': q,
            'per_page': 200,
            'query_by': 'content',
            'sort_by': '_text_match:desc',
            'include_fields': 'id'
        })

        nodes, links = coocurrence(result['hits'])
        data = links

    return Response(json.dumps(data), content_type='application/json')


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


@application.route("/vega/<path:filename>", methods=["GET"])
def vega(filename):
    return send_from_directory(os.path.join(root_dir, 'public', 'vega'), filename)
