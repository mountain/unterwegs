import redis
import typesense

from pyseaweed import WeedFS

rd = redis.Redis(host='redis', port=6379, db=1)  # for general tasks
rn = redis.Redis(host='redis', port=6379, db=2)  # for nlp related tasks

wd = WeedFS("master", 9333)  # weed-fs master address and port

ts = typesense.Client({
  'nodes': [{
    'host': 'typesense',
    'port': '8108',
    'protocol': 'http',
  }],

  'api_key': 'MUzQD3ncGDBihx6YGTBeBJ4Q',
  'connection_timeout_seconds': 2
})
