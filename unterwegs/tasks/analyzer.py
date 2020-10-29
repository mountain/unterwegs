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

    return pid

