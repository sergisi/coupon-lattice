from src.count import bob_count, alice_count, transmission_count
from src.context import Context, get_context
from src.homomorphic import keygen_homomorphic, Cyphertext
from sage.all_cmdline import (
    randint,
    Primes,
)  # import sage library
import cProfile
from concurrent.futures import ProcessPoolExecutor as Executor
import time


def protocol(ctx: Context, bob_noise=1_000_000):
    b, a = _bob_set_up(ctx)
    m_asserted, e = _protocol(b, a, ctx, bob_noise=bob_noise)
    m_expected = ctx.collapse(ctx.collapse_even(a * b + e))
    return m_expected == m_asserted


def gen_b(ctx: Context):
    for _ in range(100):
        b = ctx.r_small()
        try:
            b.inverse()
            return b
        except:
            continue
    raise ValueError("Could not generate correct b")


def _bob_set_up(ctx: Context):
    bob_count.n += 4
    b = gen_b(ctx)
    k = ctx.random_element_small(rand_function=lambda: randint(0, 1)) * (ctx.q // 2)
    e = ctx.r_small(2)
    a = (k + e) * b.inverse()
    return b, a


def _protocol(b, a, ctx, *, bob_noise=1_000_000):
    # every time that alice performs
    # the protocol, it will generate a key, so it is not
    # a set-up
    alice_count()  # counts 'a'
    key = keygen_homomorphic(alice_count, ctx)
    sa = key.enc(a, alice_count)
    transmission_count()
    bob_count.n += 3
    e = ctx.r_small(bob_noise)
    se = key.enc(e, bob_count)
    bob_ct = Cyphertext(ctx, [coef * b for coef in sa.ct]) + se
    transmission_count()
    m_asserted = ctx.collapse(key.dec(bob_ct))
    return m_asserted, e


def p_is_correct_count(ctx: Context, n=100):
    return sum(0 if protocol(ctx) else 1 for _ in range(n))


def p_is_correct(ctx: Context, n=100):
    return all(protocol(ctx) for _ in range(n))


def sum_par(f, n):
    with Executor() as executor:
        res = sum(executor.map(f, range(n)))
        return res


def search_p_protocol(start, end, ctx: Context, *, n=100):
    # returns 1000083 with
    # in 10_000 times, it failed None
    # (959322113 - 1) // 1024, (1024097281 - 1) // 1024, n=1000
    def next_midpoint(k):
        while True:
            if (1024 * k + 1) in Primes(True):
                return k
            k += 1

    end = (1024097281 - 1) // 1024
    bf = None
    for _ in range(50):
        midpoint = int((start + end) // 2)
        midpoint = next_midpoint(midpoint)
        ctx.p = 1024 * midpoint + 1
        b = p_is_correct(ctx, n)
        if b:
            end = midpoint
        else:
            start = midpoint
        yield midpoint, b
        if bf == midpoint:
            break
        bf = midpoint


def _study_singular_time(_):
    ctx = get_context()
    t0 = time.time()
    b, a = _bob_set_up(ctx)
    t1 = time.time()
    _protocol(b, a, ctx)
    t2 = time.time()
    return t1 - t0, t2 - t1


def study_time():
    with Executor() as executor:
        for t1, t2 in executor.map(_study_singular_time, range(10_000)):
            yield t1, t2


def write_study_time():
    with open("time.txt", "w") as f:
        for t1, t2 in study_time():
            print(f"{t1}, {t2}", file=f)
