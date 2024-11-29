import functools as fun
from .context import Context
import numpy as np


@fun.lru_cache
def _hash_to_point_factory(ctx: Context):
    matrix = ctx.random_matrix()

    def f(w):
        return (matrix * w) % 5

    return f


def rej_sampling(z, ca, ctx: Context):
    """I do not understand some parts of the rejection sampling
    algorithm


    ??? why two polynomials are multiplyed as vectors?
    I suppose that is transformed.
    """
    z_array = np.array(z, dtype=np.dtypes.Int32DType)
    ca_array = np.array(ca, dtype=np.dtypes.Int32DType)
    zv = z_array @ ca_array
    return (
        np.random.random()
        < (
            np.exp(
                (-2 * zv + np.linalg.norm(ca_array) ** 2) / (2 * ctx.rej_sampling_s**2)
            )
        )
        / ctx.rej_sampling_M
    )


def _gen_zs(c, ys, vectors, ctx):
    res = []
    for y, a in zip(ys, vectors):
        z = y + c * a
        if rej_sampling(z, c * a, ctx):
            return None
        res.append(z)
    return res


def ajtai_commitment(matrices, vectors, ctx, *, tries=200):
    assert len(matrices) == len(vectors)
    _hash_to_point = _hash_to_point_factory(ctx)
    for _ in range(tries):
        ys = [ctx.r_small() for _ in matrices]
        w = [A * y for A, y in zip(matrices, ys)]
        c = _hash_to_point(w)
        zs = _gen_zs(c, ys, vectors, ctx)
        if zs is not None:
            return zs
    raise Exception(f"Ajtai commitment failed on {tries}")
