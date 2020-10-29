from celery import shared_task
from celery.utils.log import get_task_logger

from unterwegs.utils.db import wd, ts, rn


logger = get_task_logger(__name__)


def init_index():
    cs = set([c['name'] for c in ts.collections.retrieve()])
    if 'articles' not in cs:
        ts.collections.create({
            'name': 'articles',
            'fields': [
                {
                  'name': 'id',
                  'type': 'string'
                },
                {
                  'name': 'title',
                  'type': 'string'
                },
                {
                  'name': 'pubdate',
                  'type': 'int32'
                },
                {
                  'name': 'authors',
                  'type': 'string[]',
                  'facet': True
                },
                {
                    'name': 'keywords',
                    'type': 'string[]',
                    'facet': True
                },
            ],
            'default_sorting_field': 'pubdate'
        })
    if 'pages' not in cs:
        ts.collections.create({
            'name': 'pages',
            'fields': [
                {
                  'name': 'id',
                  'type': 'string'
                },
                {
                  'name': 'article',
                  'type': 'string'
                },
                {
                  'name': 'index',
                  'type': 'int32'
                },
                {
                  'name': 'content',
                  'type': 'string',
                }
            ],
            'default_sorting_field': 'index'
        })


@shared_task(
    max_retries=3,
)
def analyze_bow(pid):
    from unterwegs.nlp.doc import bow

    init_index()

    page = ts.collections['pages'].documents[pid].retrieve()
    rn.zadd('bow:%s' % pid, bow(page['content']))

    return pid

