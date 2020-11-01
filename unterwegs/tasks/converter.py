import os

from celery import shared_task
from celery.utils.log import get_task_logger

from unterwegs.utils.db import wd, rd

logger = get_task_logger(__name__)


def convert(pid, page):
    from wand.image import Image, Color
    pngfname = '/data/converter/%s.png' % pid
    with Image(page.sequence[0]) as img:
        img.format = 'png'
        img.background_color = Color('white')
        img.alpha_channel = 'remove'
        img.save(filename=pngfname)
        rd.set('png:%s' % pid, wd.upload_file(pngfname))
        os.unlink(pngfname)


@shared_task(
    max_retries=3,
    soft_time_limit=5
)
def fire(fid, idx, pid):
    from io import BytesIO
    from wand.image import Image

    with Image(file=BytesIO(wd.get_file(pid)), resolution=300) as page:
        convert(pid, page.sequence[0])

    return pid

