from unterwegs.utils.db import wd, rd, rn


def coocurrence(pids):
    nodes, links = [], []
    for ix, pid in enumerate(pids):
        fid = rd.get('articleOf:page:%s' % pid)
        nodes.append({"name": pid, "group": fid, "index": ix})

    for ix, src in enumerate(pids):
        for jx, tgt in enumerate(pids):
            if ix != jx:
                dkey = 'coocur:%s:%s' % (src, tgt)
                if not rn.exists(dkey):
                    rn.zinterstore(dkey, [src, tgt], 'MIN')
                    rn.expire(dkey, 3600)
                links.append({"source": ix, "target": jx, "value": rn.zcard(dkey)})

    return nodes, links
