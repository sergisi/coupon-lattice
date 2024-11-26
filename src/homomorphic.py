from src.context import Context
from sage.all_cmdline import (
    Integer,
    randint,
    matrix,
)  # import sage library
from src.count import Count
import dataclasses as dto
import itertools
from concurrent.futures import ProcessPoolExecutor as Executor


type Message = list[int]
type MyRing = matrix


@dto.dataclass
class Cyphertext:
    ctx: Context
    ct: list[MyRing]

    def __init__(self, ctx, ct):
        self.ctx = ctx
        self.ct = list(ct)

    def __add__(self, other):
        return Cyphertext(
            self.ctx,
            [
                a + b
                for a, b in itertools.zip_longest(
                    self.ct, other.ct, fillvalue=self.ctx.ZpxQ(0)
                )
            ],
        )

    def __matmul__(self, other):
        """
        Cypertext * elem
        """
        return Cyphertext(self.ctx, [other * c for c in self.ct])

    def __mul__(self, other):
        # naive
        res = [0 for _ in range(len(self.ct) + len(other.ct) - 1)]
        for i, x in enumerate(self.ct):
            for j, y in enumerate(other.ct):
                res[i + j] += x * y
        return Cyphertext(self.ctx, res)


@dto.dataclass
class HomomorphicCryp:
    ctx: Context
    pk_a: MyRing
    pk_b: MyRing
    sk_e: MyRing
    sk_s: MyRing

    def enc(self, m: MyRing, count: Count) -> Cyphertext:
        count.n += 5
        v = self.ctx.r_small()
        e = self.ctx.r_small()
        e2 = self.ctx.r_small()
        a_ = self.pk_a * v + self.ctx.q * e
        b_ = self.pk_b * v + self.ctx.q * e2
        return Cyphertext(self.ctx, [b_ + m, -a_])

    def s_series(self):
        r = Integer(1)
        while True:
            yield r
            r *= self.sk_s

    def dec(self, ct: Cyphertext) -> Message:
        m_ = sum(a * b for a, b in zip(ct.ct, self.s_series()))
        assert m_ != 0
        p2 = self.ctx.p // 2
        m2 = (int(c) if int(c) <= p2 else int(c) - self.ctx.p for c in m_)
        return [c % self.ctx.q for c in m2]


def keygen_homomorphic(count: Count, ctx: Context):
    count.n += 3
    s = ctx.r_small()
    e = ctx.r_small()
    a = ctx.random_element()
    return HomomorphicCryp(ctx, a, a * s + ctx.q * e, e, s)


def test_homomorphic(ctx: Context):
    counter = Count()
    key = keygen_homomorphic(counter, ctx)
    m = ctx.random_element_small(rand_function=lambda: ctx.Zp(randint(0, 1)))
    ct = key.enc(m, counter)
    m_ = key.dec(ct)
    m_collapsed = ctx.collapse_even(m)
    assert m_collapsed == m_
    m2 = ctx.random_element_small(rand_function=lambda: ctx.Zp(randint(0, 1)))
    ct2 = key.enc(m2, counter)
    m_expected = ctx.collapse_even(m + m2)
    m_computed = key.dec(ct + ct2)
    assert m_expected == m_computed
    # test s_series
    s_series = [a for a, _ in zip(key.s_series(), range(3))]
    s = key.sk_s
    assert 1 == s_series[0]
    assert s == s_series[1]
    assert s * s == s_series[2]
    res = ct * ct2
    assert len(res.ct) == 3
    assert ctx.collapse_even(m * m2) == key.dec(res)
    elem_product = key.dec(Cyphertext(ctx, [m2 * c for c in ct.ct]))
    assert ctx.collapse_even(m * m2) == elem_product
    return True


def test_homomorphic_safe(ctx: Context):
    try:
        return test_homomorphic(ctx)
    except:
        return False


def test_homomorphic_times(ctx: Context, n: int = 100):
    return all(test_homomorphic_safe(ctx) for _ in range(n))
