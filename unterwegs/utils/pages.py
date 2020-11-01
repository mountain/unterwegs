import orjson as json

from unterwegs.utils.db import ts, rd, rn
from zlib import decompress, compress


def search_result(q):
    ckey = 'search:%s' % q
    result = rd.get(ckey)
    if result is not None:
        result = json.loads(decompress(result))
    else:
        result = ts.collections['pages'].documents.search({
            'q': q,
            'per_page': 200,
            'query_by': 'content',
            'sort_by': '_text_match:desc',
            'include_fields': 'id'
        })
        rd.set(ckey, compress(json.dumps(result)))
        rd.expire(ckey, 3600)

    return result


def coocurrence_nodes(hits):
    nodes = []
    for ix, hit in enumerate(hits):
        pid = hit['document']['id']
        fid = rd.get('articleOf:page:%s' % pid)
        fid = fid.decode('utf-8') if fid else 'None'
        nodes.append({"name": pid, "group": fid, "index": ix, 'highlight': hit['highlights'][0]['snippet']})

    return nodes


def coocurrence_links(hits):
    links = []
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
                    links.append({"source": ix, "target": jx, "value": int(cnt)})

    return links
