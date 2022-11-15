import orjson as json

from unterwegs.utils.db import ts, rd, rn, rc, ri
from zlib import decompress, compress


def search_result(q):
    ckey = 'search:%s' % q
    result = rc.get(ckey)
    if result is not None:
        result = json.loads(decompress(result))
    else:
        result = ts.collections['pages'].documents.search({
            'q': q,
            'per_page': 200,
            'query_by': 'content',
            'sort_by': '_text_match:desc',
            'include_fields': 'id,article',
            'drop_tokens_threshold': 0,
            'typo_tokens_threshold': 0,
            'highlight_affix_num_tokens': 50,
        })
        rc.set(ckey, compress(json.dumps(result)))
        rc.expire(ckey, 3600)

    return result


def frquency_analyze(q, hits):
    ckey = 'frequency:%s' % q
    result = rc.get(ckey)
    if result is not None:
        result = json.loads(decompress(result))
    else:
        nkey = 'freq:%s' % q
        keys = ['bow:%s' % doc['document']['id'] for doc in hits]
        rn.zunionstore(nkey, keys, 'SUM')
        rn.expire(nkey, 3600)
        freq = rn.zrange(nkey, 0, -1, desc=True, withscores=True)
        total = sum([v for k, v in freq])
        result = [{"index": ix, "term": f[0].decode('utf-8'), "total": f[1] / total} for ix, f in enumerate(freq) if ix < 300]
        rc.set(ckey, compress(json.dumps(result)))
        rc.expire(ckey, 3600)

    return result


def frequency_of(q, pid, hits):
    ckey = 'bagofwords:%s:%s' % (q, pid)
    result = rc.get(ckey)
    if result is not None:
        result = json.loads(decompress(result))
    else:
        nkey = 'bow:%s' % pid
        freq = rn.zrange(nkey, 0, -1, desc=True, withscores=True)
        total = sum([v for k, v in freq])
        freq = {k.decode('utf-8'): v / total for k, v in freq}
        base = frquency_analyze(q, hits)
        result = []
        for item in base:
            ix, term, total = item['index'], item['term'], item['total']
            if term in freq:
                result.append({"index": ix, "term": term, "total": total, "page": freq[term]})
        rc.set(ckey, compress(json.dumps(result)))
        rc.expire(ckey, 3600)

    return result


def coocurrence_nodes(q, hits):
    ckey = 'nodes:%s' % q
    result = rc.get(ckey)
    if result is not None:
        result = json.loads(decompress(result))
    else:
        result = []
        for ix, hit in enumerate(hits):
            pid = hit['document']['id']
            fid = rd.get('articleOf:page:%s' % pid)
            fid = fid.decode('utf-8') if fid else 'None'
            result.append({"name": pid, "group": fid, "index": ix, 'highlight': hit['highlights'][0]['snippet']})
        rc.set(ckey, compress(json.dumps(result)))
        rc.expire(ckey, 3600)

    return result


def coocurrence_links(q, hits):
    ckey = 'links:%s' % q
    result = rc.get(ckey)
    if result is not None:
        result = json.loads(decompress(result))
    else:
        result = []
        total, avg = 0, 0
        for ix, ih in enumerate(hits):
            src = ih['document']['id']
            for jx, jh in enumerate(hits):
                tgt = jh['document']['id']
                if ix != jx:
                    skey, tkey, dkey = 'bow:%s' % src, 'bow:%s' % tgt, 'coocur:%s:%s' % (src, tgt)
                    if not rn.exists(dkey):
                        cnt = rn.zinterstore(dkey, [skey, tkey], 'MIN')
                        rn.expire(dkey, 3600 * 24 * 7)
                    else:
                        cnt = rn.zcard(dkey)
                    if cnt > 0:
                        total += cnt
                        result.append({"source": ix, "target": jx, "value": int(cnt)})
        rc.set(ckey, compress(json.dumps(result)))
        rc.expire(ckey, 3600)

    return result


def recommend(pid):
    if not ri.exist('rcm:%s' % pid):
        result = []
    else:
        result = ri.zrange('rcm:%s' % pid, 0, -1)

    result = [page_id.decode('utf-8') for page_id in result[:6]]
    return list(result)
