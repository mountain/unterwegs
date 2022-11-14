import numpy as np

from scipy.spatial.distance import squareform, pdist
from scipy.special import xlogy

from unterwegs.nlp.emb import sinkhorn_knopp as skp

"""
DOSNES was published and first implemented by Yao Lu in 2016
This version was a modification of the original implementation by Mingli Yuan

Implementation of the Doubly Stochastic Neighbor Embedding on Spheres algorithm published by Yao Lu in Sep. 2016
https://arxiv.org/abs/1609.01977

This algorithm is used to embbed datas on a 3-Dimensional Sphere. It's a translation in "sklearn" of the repo
https://github.com/yaolubrain/DOSNES but in Python

Thanks to btaba for the implementation of sinkhorn_knopp algorithm: https://github.com/btaba/sinkhorn_knopp
"""

no_dims = 3            # dimension of the embedding
max_iter_skp = 1e3     # maximum number of iterations for Sinkhorn-Knopp algorithm
epsilon_skp = 1e-3     # stopping Criterion for the Sinkhorn–Knopp Algorithm
momentum = 0.5         # weight used during iteration process to update position
final_momentum = 0.3   # weight used during iteration process to update position after mom_switch_iter
mom_switch_iter = 250  # trigger to switch from momentum to final_momentum
max_iter = 1000        # number of iterations to optimise embedding
learning_rate = 1      # learning rate used to update position of points in the embedded space
min_gain = 0.01        # value used to clip negative gains (must be > 0)
random_state = None    # random State used to generate the initial y matrix
verbose_freq = 10      # number of iterations between every print of the cost function

np.random.seed(random_state)
MACHINE_EPSILON = np.finfo(np.double).eps
sk = skp.SinkhornKnopp(max_iter=max_iter_skp, epsilon=epsilon_skp)


def doubly_stochastic(dmatrix):
    return sk.fit(np.exp(-dmatrix ** 2 / 2))


def embed(ds):
    global momentum
    n = ds.shape[0]
    ps = doubly_stochastic(ds)
    print("Start Embedding")

    ps[np.diag_indices_from(ps)] = 0.
    ps = (ps + ps.T) / 2
    ps = np.maximum(ps / ps.sum(), MACHINE_EPSILON)
    const = np.sum(xlogy(ps, ps))

    ydata = 1e-4 * np.random.random(size=(n, no_dims))
    y_incs = np.zeros_like(ydata)
    gains = np.ones_like(ydata)

    for iter in range(max_iter):
        sum_ydata = np.sum(ydata ** 2, axis=1)
        num = 1. / (1 + sum_ydata + sum_ydata[np.newaxis].T + -2 * np.dot(ydata, ydata.T))
        num[np.diag_indices_from(num)] = 0.

        qs = np.maximum(num / num.sum(), MACHINE_EPSILON)
        ls = (ps - qs) * num

        t = np.diag(ls.sum(axis=0)) - ls
        y_grads = 4 * np.dot(t, ydata)

        inc = (np.sign(y_grads) != np.sign(y_incs))
        dec = np.invert(inc)
        gains[inc] += 0.2
        gains[dec] *= 0.8
        gains = np.clip(gains, a_min=min_gain, a_max=np.inf)

        y_incs = momentum * y_incs - learning_rate * gains * y_grads
        ydata += y_incs
        ydata -= ydata.mean(axis=0)

        rad = np.sqrt(np.sum(ydata ** 2, axis=1))
        r_mean = np.mean(rad)
        ydata *= (r_mean / rad).reshape(-1, 1)

        if iter == mom_switch_iter:
            momentum = final_momentum

        if iter % verbose_freq == 0:
            cost = const - np.sum(xlogy(ps, qs))
            print("Iteration {} : error is {}".format(iter, cost))

    return ydata / np.sqrt(np.sum(ydata ** 2, axis=1)).reshape(-1, 1)
