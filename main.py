"""
Main function to abstact different metrics of the protocol

"""

from src.context import get_context
from src.protocol import set_up
import cProfile
import time


def main(tokens: int = 1000):
    """
    Generates 1000 coupons and then uses them. Prints the time of
    the set-up, the generation, and the redemption.
    """
    t0 = time.time()
    ctx = get_context()
    protocol = set_up(ctx)
    t1 = time.time()
    token_chain = protocol.customer.generate_n_coupons(protocol.issuer, tokens)
    t2 = time.time()
    while token_chain is not None:
        token_chain = protocol.customer.redeem_token(protocol.issuer, token_chain)
    t3 = time.time()
    print(t1 - t0, t2 - t1, t3 - t2)


def generate_noise_one():
    ctx = get_context()
    a = ctx.r_small()
    b = ctx.r_small_vector()
    c = ctx.r_small_vector()
    v = a + b * c
    p = ctx.p
    q2 = p // 2
    v1 = (int(coef) % p for coef in v)
    v2 = (coef if coef < q2 else coef-p for coef in v1)
    v3 = (abs(coef) for coef in v2)
    return max(v3)

def generate_noise(times: int = 1000):
    return max((generate_noise_one() for _ in range(times)))


if __name__ == "__main__":
    main()
    # cProfile.run('main()')
