import time
import uuid

import unterwegs.tasks.uploader as upldr

from flask import request
from uuid import uuid5
from .app import create_app


application = create_app()


@application.route('/')
def home():
    return 'Hello World!'


@application.route('/search')
def search():
    return 'Hello World!'


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
