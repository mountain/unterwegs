import os
import time
import uuid
import json

import unterwegs.tasks.uploader as upldr

from flask import request, render_template, send_from_directory
from uuid import uuid5
from .app import create_app
from unterwegs.utils.db import wd, rd, ts
from unterwegs.utils.coocur import coocurrence


specs = {}
application = create_app()

root_dir = os.path.dirname(os.getcwd())


def load_spec(key):
    with open('/web/unterwegs/spec/%s.json' % key) as j:
        specs[key] = json.load(j)


load_spec('fdl')


@application.route('/search/<string:q>')
def search(q):
    result = ts.collections['pages'].documents.search({
        'q': q,
        'per_page': 200,
        'query_by': 'content',
        'sort_by': '_text_match:desc',
        'include_fields': 'id'
    })

    highlights = {h['document']['id']: h['highlights'][0]['snippet'] for h in result['hits']}
    nodes, links = coocurrence(list([h['document']['id'] for h in result['hits']]))
    nodes = [{'name': nd['name'], 'group': nd['group'], 'index': nd['index'], 'highlight': highlights[nd['name']]} for nd in nodes]

    spec = specs['fdl']
    spec['data'][0]['values'] = nodes
    spec['data'][1]['values'] = links

    return render_template('vega.html', query=q, spec=spec)


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
