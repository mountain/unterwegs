import numpy as np

from scipy.spatial.distance import pdist, squareform
from unterwegs.nlp.doc import dosnes
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
    get_task_logger('recommender').info('start index %s:%s' % (pid, qid))

    if ri.exists('wmd:%s:%s' % (pid, qid)) == 0:
        p = rn.zrange('bow:%s' % pid, 0, -1, withscores=True)
        q = rn.zrange('bow:%s' % qid, 0, -1, withscores=True)
        d = wmd(p, q)
        ri.set('wmd:%s:%s' % (pid, qid), '%0.9f' % d)
        ri.set('wmd:%s:%s' % (qid, pid), '%0.9f' % d)


@shared_task(
    max_retries=3,
    soft_time_limit=5
)
def embed():
    get_task_logger('recommender').info('start embed')

    pids = sorted(list([key.decode('utf-8').split(':')[1] for key in rn.keys('bow:*')]))
    plen = len(pids)
    dmatrix = np.zeros((plen, plen), dtype=np.double)
    for ix, p in enumerate(pids):
        for jx, q in enumerate(pids):
            dmatrix[ix, jx] = float(ri.get('wmd:%s:%s' % (p, q)))

    embedding = dosnes.embed(dmatrix)
    embd = squareform(pdist(embedding, metric='cosine'))
    for ix, p in enumerate(pids):
        for jx, q in enumerate(pids):
            d = embd[ix, jx]
            ri.zadd('rcm:%s' % p, {q: d})
            ri.zadd('rcm:%s' % q, {p: d})
            ri.zremrangebyrank('rcm:%s' % p, 6, -1)
            ri.zremrangebyrank('rcm:%s' % q, 6, -1)

