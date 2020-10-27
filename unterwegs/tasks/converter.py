import os

from io import BytesIO
from wand.image import Image
from celery import shared_task
from celery.utils.log import get_task_logger

from unterwegs.utils.db import wd, rd

logger = get_task_logger(__name__)


def convert(pid, page, width, height, key):
    pngfname = '/data/converter/%s.png' % pid
    page.resize(width=width, height=height)
    page.save(filename=pngfname)
    rd.set('%s:%s' % (key, pid), wd.upload_file(pngfname))
    os.unlink(pngfname)


@shared_task(
    max_retries=3,
    soft_time_limit=5
)
def fire(fid, idx, pid):
    with Image(file=BytesIO(wd.get_file(pid)), resolution=120) as page:
        w, h = page.size
        convert(pid, page, 75, int(75 / w * h), 'thumbnail:small:horizontal')
        convert(pid, page, 75, int(75 / h * w), 'thumbnail:small:vertical')
        convert(pid, page, 200, int(200 / w * h), 'thumbnail:big:horizontal')
        convert(pid, page, 200, int(200 / h * w), 'thumbnail:big:vertical')

    return pid

