from .context import Context
from sage.all import Integer
import numpy as np
import functools


@functools.lru_cache
def get_context():
    return Context(
        p=Integer(12 * 1024 + 1),
        degree=1024,
        m=2,
        cbd_noise=2,
        small_degree=1024,
        small_max_value=2,
        rej_sampling_module=5,
    )


@functools.lru_cache(maxsize=1)
def gotta_go_fast_context():
    return Context(
        p=Integer(12 * 1024 + 1),
        degree=64,
        m=2,
        cbd_noise=2,
        small_degree=64,
        small_max_value=2,
        rej_sampling_module=5,
    )


##########################
def to_numpy(f):
    return np.array([np.array(list(x), dtype=np.int_) for x in f.coefficients()])
