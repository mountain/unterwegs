import requests

from urllib.parse import quote_plus
from celery import shared_task
from celery.utils.log import get_task_logger
from unterwegs.utils.db import ri, sb, lookup


logger = get_task_logger(__name__)


@shared_task(
    max_retries=3,
    soft_time_limit=5
)
def index(pid, page_content):
    get_task_logger('recommender').info('start %s' % pid)

    page_content = page_content.replace('\n', ' ').strip()
    page_content = page_content.replace('+', ' ').strip()
    page_content = page_content.replace('-', ' ').strip()
    page_content = page_content.replace('?', ' ').strip()
    page_content = page_content.replace('[', '').strip()
    page_content = page_content.replace(']', '').strip()
    page_content = page_content.replace('\'', '').strip()
    page_content = page_content.replace('cid', '').strip()
    page_content = ' '.join([wd for wd in page_content.split(' ') if len(wd) > 2])

    encoded = quote_plus(page_content)
    resp = requests.get('http://%s:%s/topics/%s' % (lookup("lda"), '7777', encoded))
    if resp.status_code == 200:
        data = resp.json()
        if 'topics' in data:
            vec = data['topics']

            if not ri.hexists('pid2vid', pid):
                vid = ri.incr('serial:vid')
                ri.hset('pid2vid', pid, vid)
                ri.hset('vid2pid', vid, pid)
            else:
                vid = ri.hget('pid2vid', pid)

            vid = int(vid)
            sb.execute_command('vadd', 'page', vid, *vec)
            get_task_logger('recommender').info('finish %s' % pid)
