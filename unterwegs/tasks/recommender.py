import requests

from celery import shared_task
from celery.utils.log import get_task_logger
from unterwegs.utils.db import rn, ri
from unterwegs.nlp.doc import wmd


logger = get_task_logger(__name__)


@shared_task(
    max_retries=3,
    soft_time_limit=5
)
def index(pid, qid):
    get_task_logger('recommender').info('start %s:%s' % (pid, qid))

    if ri.exists('wmd:%s:%s' % (pid, qid)) == 0:
        p = rn.zrange('bow:%s' % pid, 0, -1, withscores=True)
        q = rn.zrange('bow:%s' % qid, 0, -1, withscores=True)
        d = wmd(p, q)
        ri.set('wmd:%s:%s' % (pid, qid), '%0.9f' % d)
        ri.set('wmd:%s:%s' % (qid, pid), '%0.9f' % d)
        ri.zadd('rcm:%s' % pid, {qid: d})
        ri.zadd('rcm:%s' % qid, {pid: d})
        ri.zremrangebyrank('rcm:%s' % pid, 6, -1)
        ri.zremrangebyrank('rcm:%s' % qid, 6, -1)
