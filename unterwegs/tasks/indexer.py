import typesense

from pyseaweed import WeedFS
from celery import shared_task
from celery.utils.log import get_task_logger
from unterwegs.utils.pdf import pdf2meta, pdf2txt


logger = get_task_logger(__name__)

wd = WeedFS("master", 9333)  # weed-fs master address and port


client = typesense.Client({
  'nodes': [{
    'host': 'typesense',
    'port': '8108',
    'protocol': 'http',
  }],

  'api_key': 'MUzQD3ncGDBihx6YGTBeBJ4Q',
  'connection_timeout_seconds': 2
})


def init_index():
    cs = set([c['name'] for c in client.collections.retrieve()])
    if 'articles' not in cs:
        client.collections.create({
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
        client.collections.create({
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
    init_index()

    meta = pdf2meta(wd.get_file(fid))
    document = {
        'id': fid,
        'title': meta['title'],
        'authors': meta['authors'],
        'keywords': meta['keywords']
    }

    client.collections['articles'].documents.create(document)

    return fid


@shared_task(
    max_retries=3,
)
def index_page(fid, pid, idx):
    init_index()

    content = pdf2txt(wd.get_file(fid))
    document = {
        'id': pid,
        'article': fid,
        'index': idx,
        'content': content
    }

    client.collections['pages'].documents.create(document)

    return fid, pid, idx