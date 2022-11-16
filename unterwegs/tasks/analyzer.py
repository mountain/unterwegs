import unterwegs.tasks.recommender as rcmdr

from celery import shared_task
from celery.utils.log import get_task_logger

from unterwegs.utils.db import ts, rn

logger = get_task_logger(__name__)


@shared_task(
    max_retries=3,
)
def analyze_bow(pid):
    from unterwegs.nlp.doc import bow

    page = ts.collections['pages'].documents[pid].retrieve()
    rn.zadd('bow:%s' % pid, bow(page['content']))
    for key in rn.keys('bow:*'):
        qid = key.decode('utf-8').split(':')[1]
        if qid != pid:
            rcmdr.index.delay(pid, qid)

    rcmdr.embed.delay()

    return pid

