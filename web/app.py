import time
import uuid
import tasks.uploader as upldr

from flask import Flask, request
from uuid import uuid5

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 40
app.config['UPLOAD_EXTENSIONS'] = ['.pdf']


@app.route('/')
def hello():
    upldr.fire(time.time())
    return 'Hello World!'


@app.route("/upload", methods=["POST"])
def upload():
    upload_key = uuid5(uuid.NAMESPACE_URL, str(time.time())).hex
    target = "/uploads/{}".format(upload_key)
    for upload in request.files.getlist("upload"):
        filename = upload.filename.rsplit("/")[0]
        destination = "-".join([target, filename])
        upload.save(destination)
        upldr.fire.delay(destination)

    return 'OK'
