import functools as fun
import dataclasses as dto
import itertools
from typing import Any

from sage.all import vector
from .context import Context
import numpy as np


type PolyVec = Any
type Poly = Any


@fun.lru_cache
def _hash_to_point_factory(matrix, module):
    def f(w: PolyVec):
        res = matrix * vector([1, w])
        return [int(r) % module for r in res]

    return f


def _to_array(vs: PolyVec, ctx: Context):
    return np.array(
        list(itertools.chain.from_iterable(ctx.collapse_even(v) for v in vs)),
        dtype=np.int32,
    )


def rej_sampling(z: PolyVec, ca: PolyVec, ctx: Context):
    """I do not understand some parts of the rejection sampling
    algorithm


    ??? why two polynomials are multiplyed as vectors?
    I suppose that is transformed.

    Okey, actually, the vectors were, in fact, vectors of poly.
    No clue what it means to have this computed.
    """
    z_array = _to_array(z, ctx)
    ca_array = _to_array(ca, ctx)
    zv = z_array @ ca_array
    return zv >= 0 and (
        np.random.random()
        < (
            np.exp(
                (-2 * zv + np.linalg.norm(ca_array) ** 2) / (2 * ctx.rej_sampling_s**2)
            )
        )
        / 3  # rej_sampling_M is always 3 and only used once.
    )


def _gen_zs(c, ys, vectors, ctx):
    res = []
    for y, a in zip(ys, vectors):
        z = y + c * a
        if rej_sampling(z, c * a, ctx):
            return None
        res.append(z)
    return res


def norm(z: PolyVec, ctx: Context):
    return np.linalg.norm(_to_array(z, ctx))


@dto.dataclass
class AjtaiCommitment:
    w: list
    zs: list
    matrices: list
    t: Poly
    c: Poly
    ctx: Context

    def __call__(self) -> bool:
        return (
            all(norm(z, self.ctx) <= self.ctx.rej_sampling_bound for z in self.zs)
            and sum(A * z for A, z in zip(self.matrices, self.zs))
            == self.w + self.c * self.t
        )


def ajtai_commitment(
    matrices: list, vectors: list, ctx: Context, *, tries: int = 200
) -> AjtaiCommitment:
    """
    Creates an Ajtai Commimement Correctly
    """
    assert len(matrices) == len(vectors)
    _hash_to_point = _hash_to_point_factory(
        ctx.random_vector(), ctx.rej_sampling_module
    )
    for _ in range(tries):
        ys = [ctx.r_small_vector() for _ in matrices]
        w = sum(A * y for A, y in zip(matrices, ys))
        c = ctx.ZpxQ(_hash_to_point(w))
        zs = _gen_zs(c, ys, vectors, ctx)
        if zs is not None:
            return AjtaiCommitment(
                w, zs, matrices, sum(a * t for a, t in zip(matrices, vectors)), c, ctx
            )
    raise Exception(f"Ajtai commitment failed on {tries}")
