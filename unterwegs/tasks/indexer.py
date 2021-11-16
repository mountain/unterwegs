from celery import shared_task
from celery.utils.log import get_task_logger

import unterwegs.tasks.analyzer as anlzr
import unterwegs.tasks.recommender as rcmdr

from unterwegs.utils.db import wd, ts


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
def index_article(fid):
    from unterwegs.utils.pdf import pdf2meta
    init_index()

    meta = {}
    try:
        meta = pdf2meta(wd.get_file(fid))
    except Exception:
        get_task_logger('indexer').info(fid)

    meta['pubdate'] = 0
    if 'title' not in meta:
        meta['title'] = '?'
    if 'authors' not in meta:
        meta['authors'] = ['?']
    if 'keywords' not in meta:
        meta['keywords'] = ['?']

    document = {
        'id': fid,
        'title': meta['title'],
        'authors': meta['authors'],
        'keywords': meta['keywords'],
        'pubdate': meta['pubdate']
    }

    try:
        ts.collections['articles'].documents.create(document)
    except Exception:
        get_task_logger('indexer').info(fid)

    return fid


@shared_task(
    max_retries=3,
)
def index_page(fid, pid, idx):
    from unterwegs.utils.pdf import pdf2txt

    init_index()

    content = pdf2txt(wd.get_file(pid))
    content = content.replace('\n', ' ').strip()
    content = content.replace('+', ' ').strip()
    content = content.replace('-', ' ').strip()
    content = content.replace('?', ' ').strip()
    content = content.replace('[', '').strip()
    content = content.replace(']', '').strip()
    content = content.replace('\'', '').strip()
    content = content.replace('cid', '').strip()
    content = ' '.join([wd for wd in page_content.split(' ') if len(wd) > 2])

    document = {
        'id': pid,
        'article': fid,
        'index': idx,
        'content': content
    }

    ts.collections['pages'].documents.create(document)
    rcmdr.index.delay(pid, content)
    anlzr.analyze_bow.delay(pid)

    return fid, pid, idx
