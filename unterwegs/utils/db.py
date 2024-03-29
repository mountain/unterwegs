import redis
import typesense
import socket

from pyseaweed import WeedFS


def lookup(name):
    try:
        socket.gethostbyname(name)
        return name
    except Exception:
        return 'localhost'


rd = redis.Redis(host=lookup('redis'), port=6379, db=1)  # for general tasks
rn = redis.Redis(host=lookup('redis'), port=6379, db=2)  # for nlp related tasks
rc = redis.Redis(host=lookup('redis'), port=6379, db=3)  # for cache only
ri = redis.Redis(host=lookup('redis'), port=6379, db=4)  # for index only

wd = WeedFS(lookup("master"), 9333)  # weed-fs master address and port

ts = typesense.Client({
  'nodes': [{
    'host': lookup('typesense'),
    'port': '8108',
    'protocol': 'http',
  }],

  'api_key': 'MUzQD3ncGDBihx6YGTBeBJ4Q',
  'connection_timeout_seconds': 2
})
