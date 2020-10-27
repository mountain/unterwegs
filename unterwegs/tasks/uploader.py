import os
import time
import hashlib

import unterwegs.tasks.splitter as spltr
import unterwegs.tasks.indexer as indxr

from celery import shared_task
from celery.utils.log import get_task_logger
from unterwegs.utils.db import wd, rd


logger = get_task_logger(__name__)


def excerpt_md5hash(fname):
    with open(fname, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


@shared_task(
    max_retries=3,
    soft_time_limit=5
)
def fire(fname):
    hash = excerpt_md5hash(fname)
    if rd.hexists('hash', hash) == 0:
        logger.info("uploading %s" % fname)
        fid = wd.upload_file(fname)

        logger.info("recording %s %s", hash, fid)
        rd.hset('hash', hash, fid)
        rd.zadd('log', {
            fid: time.time()
        })

        logger.info("invoke indexer %s", fid)
        indxr.index_article.delay(fid)
        logger.info("invoke splitter %s", fid)
        spltr.fire.delay(fid)

    os.unlink(fname)
    logger.info("finish %s" % fname)

    return fname

