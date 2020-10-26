import redis

import unterwegs.tasks.converter as cnvtr
import unterwegs.tasks.indexer as indxr

from io import BytesIO
from celery import shared_task
from celery.utils.log import get_task_logger
from pyseaweed import WeedFS
from unterwegs.utils.pdf import pdf_pages

logger = get_task_logger(__name__)

wd = WeedFS("master", 9333)  # weed-fs master address and port
rd = redis.Redis(host='redis', port=6379, db=1)


@shared_task(
    max_retries=3,
    soft_time_limit=5
)
def fire(fid):
    logger.info("start splitting %s" % fid)
    for idx, page in pdf_pages(wd.get_file(fid)):
        with BytesIO(page) as in_file:
            pid = wd.upload_file(stream=in_file, name='%s-%s.pdf' % (fid, idx))
            logger.info("uploaded page %s[%s]: %s",fid, idx, pid)

            rd.zadd('article:%s' % fid, {
                pid: idx
            })
            rd.set('articleOf:page:%s' % pid, fid)
            logger.info("recorded page %s[%s]: %s", fid, idx, pid)

            cnvtr.fire.delay(fid, idx, pid)
            logger.info("invoked converter %s[%s]: %s" , fid, idx, pid)
            indxr.index_page.delay(fid, pid, idx)
            logger.info("invoked indexer %s[%s]: %s", fid, idx, pid)

    logger.info("finish splitting %s" % fid)
    return fid

