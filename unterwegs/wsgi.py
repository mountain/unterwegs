import time
import uuid

import unterwegs.tasks.uploader as upldr

from flask import request
from uuid import uuid5
from .app import create_app
from unterwegs.utils.db import wd, rd, ts


application = create_app()


@application.route('/')
def home():
    return 'Hello World!'


@application.route('/search/<string:q>')
def search(q):
    result = ts.collections['pages'].documents.search({
        'q': q,
        'query_by': 'content',
        'sort_by': '_text_match:desc'
    })

    return str(result['found'])


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
