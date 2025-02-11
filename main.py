"""
Main function to abstact different metrics of the protocol

"""

from src.context import get_context
from src.protocol import set_up
import cProfile
import time


def main(tokens: int = 10):
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


if __name__ == "__main__":
    cProfile.run('main()')
