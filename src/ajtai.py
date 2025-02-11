import functools as fun
import dataclasses as dto
import itertools
from typing import Any

from sage.all import vector
from .context import Context
import numpy as np
from Crypto.Hash import SHAKE256

type PolyVec = Any
type Poly = Any

def _message_to_bytes(message: Poly, ctx: Context):
    for v in (int(c) for c in message):
        while v != 0:
            yield v % 256
            v = v >> 8


def hash_to_point(message, ctx: Context):
    """
    Hash a message to a point in Z[x] mod(Phi, q).
    Inspired by the Parse function from NewHope.
    """
    n = ctx.degree
    if ctx.p > (1 << 16):
        raise ValueError("The modulus is too large")

    k = (1 << 16) // ctx.p
    # Create a SHAKE object and hash the salt and message.
    shake = SHAKE256.new()
    shake.update(ctx.salt)
    message_bytes = bytes(_message_to_bytes(message, ctx))
    shake.update(message_bytes)
    # Output pseudorandom bytes and map them to coefficients.
    hashed = [0 for i in range(n)]
    i = 0
    while i < n:
        # Takes 2 bytes, transform them in a 16 bits integer
        twobytes = shake.read(1)
        elt = twobytes[0]
        # Implicit rejection sampling
        if elt < k * ctx.p:
            hashed[i] = elt % ctx.rej_sampling_module
            i += 1
    return hashed


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
    matrices: list, vectors: list, ctx: Context, *, tries: int = 500
) -> AjtaiCommitment:
    """
    Creates an Ajtai Commimement Correctly
    """
    assert len(matrices) == len(vectors)
    for _ in range(tries):
        ys = [ctx.r_small_vector() for _ in matrices]
        w = sum(A * y for A, y in zip(matrices, ys))
        c = ctx.ZpxQ(hash_to_point(w, ctx))
        zs = _gen_zs(c, ys, vectors, ctx)
        if zs is not None:
            return AjtaiCommitment(
                w, zs, matrices, sum(a * t for a, t in zip(matrices, vectors)), c, ctx
            )
    raise Exception(f"Ajtai commitment failed on {tries}")
