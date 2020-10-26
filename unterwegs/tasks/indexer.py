import typesense

from celery import shared_task


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
    pass


@shared_task(
    max_retries=3,
    soft_time_limit=5
)
def index_article(fid):
    init_index()
    return fid


@shared_task(
    max_retries=3,
    soft_time_limit=5
)
def index_page(fid, pid, idx):
    init_index()
    return fid, pid, idx
