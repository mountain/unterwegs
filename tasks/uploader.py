import os
import logging
import tasks as ts

from celery.utils.log import get_task_logger
from pyseaweed import WeedFS

logger = get_task_logger(__name__)

wd = WeedFS("master", 9333) # weed-fs master address and port


@ts.app.task
def fire(fname):
    logger.info("start uploading %s" % fname)
    fid = wd.upload_file(fname)
    furl = wd.get_file_url(fid)
    logger.info("finish uploading %s: %s, %s" % (fname, fid, furl))
    os.unlink(fname)

    return fname

