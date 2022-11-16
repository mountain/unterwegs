import numpy as np
import collections
import spacy

from scipy.spatial.distance import pdist, squareform
from pyemd import emd


nlp = spacy.load("en_core_web_md")


def bow(text: str):
    bag = collections.OrderedDict()
    d = nlp(text.replace('\n', ' ').strip())

    for tk in d:
        lexeme = d.vocab[tk.text]
        if lexeme.is_alpha and not lexeme.is_stop:
            txt = tk.text.strip()
            if len(txt) > 2:
                if txt not in bag:
                    bag[txt] = 0
                bag[txt] += 1

    for nc in d.noun_chunks:
        chunk = nc.text.strip()
        if len(chunk.split(' ')) > 1:
            if chunk not in bag:
                bag[chunk] = 0
            bag[chunk] += 1

    return bag


def nbow(bag: dict, lvoc: int, voc: list):
    d = np.zeros(lvoc, dtype=np.double)
    for ix, tm in enumerate(voc):
        if tm in bag:
            d[ix] = bag[tm]
    return d / d.sum()


def wmd(bag1: dict, bag2: dict):
    vec = nlp.vocab.vectors
    idx = nlp.vocab.strings
    voc = sorted(list(set(bag1.keys()).union(set(bag2.keys()))))
    lvoc = len(voc)

    def norm(t):
        h = idx[t]
        r = vec.key2row[h]
        return np.array(vec.data[r] / np.linalg.norm(vec.data[r]))

    dmatrix = np.zeros((lvoc, lvoc), dtype=np.double)
    for ix, t1 in enumerate(voc):
        for jx, t2 in enumerate(voc):
            if t1 in idx and idx[t1] in vec.key2row and t2 in idx and idx[t2] in vec.key2row:
                dst = np.sum(norm(t1) * norm(t2))
                dmatrix[ix, jx] = dst
                dmatrix[jx, ix] = dst

    d1 = nbow(bag1, lvoc, voc)
    d2 = nbow(bag2, lvoc, voc)
    return emd(d1, d2, dmatrix)


if __name__ == '__main__':
    import unterwegs.nlp.emb.dosnes as dosnes
    import arxiv as arx
    import pyvista as pv

    k = 3
    texts = []
    papers = []

    search = arx.Search(
        query="entanglement",
        max_results=k,
        sort_by=arx.SortCriterion.Relevance
    )
    for result in search.results():
        print(result.entry_id)
        texts.append("%s; %s; %s; %s" % (result.title, result.authors, result.summary, result.categories))
        papers.append(bow(texts[-1]))

    search = arx.Search(
        query="sheaves",
        max_results=k,
        sort_by=arx.SortCriterion.Relevance
    )
    for result in search.results():
        print(result.entry_id)
        texts.append("%s; %s; %s; %s" % (result.title, result.authors, result.summary, result.categories))
        papers.append(bow(texts[-1]))

    search = arx.Search(
        query="language model",
        max_results=k,
        sort_by=arx.SortCriterion.Relevance
    )
    for result in search.results():
        print(result.entry_id)
        texts.append("%s; %s; %s; %s" % (result.title, result.authors, result.summary, result.categories))
        papers.append(bow(texts[-1]))

    search = arx.Search(
        query="fisher information",
        max_results=k,
        sort_by=arx.SortCriterion.Relevance
    )
    for result in search.results():
        print(result.entry_id)
        texts.append("%s; %s; %s; %s" % (result.title, result.authors, result.summary, result.categories))
        papers.append(bow(texts[-1]))

    search = arx.Search(
        query="phylogenetics",
        max_results=k,
        sort_by=arx.SortCriterion.Relevance
    )
    for result in search.results():
        print(result.entry_id)
        texts.append("%s; %s; %s; %s" % (result.title, result.authors, result.summary, result.categories))
        papers.append(bow(texts[-1]))

    search = arx.Search(
        query="poverty",
        max_results=k,
        sort_by=arx.SortCriterion.Relevance
    )
    for result in search.results():
        print(result.entry_id)
        texts.append("%s; %s; %s; %s" % (result.title, result.authors, result.summary, result.categories))
        papers.append(bow(texts[-1]))

    search = arx.Search(
        query="parser",
        max_results=k,
        sort_by=arx.SortCriterion.Relevance
    )
    for result in search.results():
        print(result.entry_id)
        texts.append("%s; %s; %s; %s" % (result.title, result.authors, result.summary, result.categories))
        papers.append(bow(texts[-1]))

    n = len(papers)
    X = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dst = wmd(papers[i], papers[j])
            print(i, j, dst)
            X[i, j] = dst
            X[j, i] = dst

    for ix in range(len(papers)):
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(ix, texts[ix])
        print('-----------------------------------------------------')
        for jx in np.argsort(X[ix])[:5]:
            if ix != jx:
                print(jx, X[ix, jx])
                print(jx, texts[jx])
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++')

    embedding = dosnes.embed(X)
    dist = squareform(pdist(embedding, metric='cosine'))
    for ix in range(len(papers)):
        print('=====================================================')
        print(ix, texts[ix])
        print('-----------------------------------------------------')
        for jx in np.argsort(dist[ix])[:5]:
            if ix != jx:
                print(jx, dist[ix, jx])
                print(jx, texts[jx])
        print('=====================================================')

    plotter = pv.Plotter()
    plotter.add_mesh(pv.PolyData(embedding[0*k:1*k]), color='blue', point_size=10.0, render_points_as_spheres=True)
    plotter.add_mesh(pv.PolyData(embedding[1*k:2*k]), color='maroon', point_size=10.0, render_points_as_spheres=True)
    plotter.add_mesh(pv.PolyData(embedding[2*k:3*k]), color='red', point_size=10.0, render_points_as_spheres=True)
    plotter.add_mesh(pv.PolyData(embedding[3*k:4*k]), color='yellow', point_size=10.0, render_points_as_spheres=True)
    plotter.add_mesh(pv.PolyData(embedding[4*k:5*k]), color='green', point_size=10.0, render_points_as_spheres=True)
    plotter.add_mesh(pv.PolyData(embedding[5*k:6*k]), color='violet', point_size=10.0, render_points_as_spheres=True)
    plotter.add_mesh(pv.PolyData(embedding[6*k:7*k]), color='black', point_size=10.0, render_points_as_spheres=True)
    plotter.add_mesh(pv.Sphere(radius=0.98))
    plotter.show_grid()
    plotter.show()
