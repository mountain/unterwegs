import math

from unterwegs.utils.db import ts, rd, rn


def coocurrence(pids):
    nodes, links = [], []
    for ix, pid in enumerate(pids):
        fid = rd.get('articleOf:page:%s' % pid)
        fid = fid.decode('utf-8') if fid else 'None'
        nodes.append({"name": pid, "group": fid, "index": ix})

    for ix, src in enumerate(pids):
        for jx, tgt in enumerate(pids):
            if ix != jx:
                skey, tkey, dkey = 'bow:%s' % src, 'bow:%s' % tgt, 'coocur:%s:%s' % (src, tgt)
                if not rn.exists(dkey):
                    cnt = rn.zinterstore(dkey, [skey, tkey], 'MIN')
                    rn.expire(dkey, 3600)
                else:
                    cnt = rn.zcard(dkey)
                if cnt > 0:
                    links.append({"source": ix, "target": jx, "value": int(cnt)})

    return nodes, links
