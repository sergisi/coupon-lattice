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
    # NOTE: 
    # - ISSUER: 5 vectors, 1 element
    # - Customer: 5 vectors
    # NONE COMMUNICATION ?
    protocol = set_up(ctx)
    t1 = time.time()
    # NOTE: 
    # - OPEN: 4 vectors
    # - CLOSED: 2+2 vectors ceil
    # Communication
    # NIZK -> 
    # <- AEScy
    token_chain = protocol.customer.generate_n_coupons(protocol.issuer, tokens)
    t2 = time.time()
    while token_chain is not None:
        # NOTE: Memory 
        # - NIZK Commitment
        # - key = 256 bits
        # - one element
        # Communication:
        # - NIZK (3 vectors) ->
        # - <- r (element)
        token_chain = protocol.customer.redeem_token(protocol.issuer, token_chain)
    t3 = time.time()
    print(t1 - t0, t2 - t1, t3 - t2)


if __name__ == "__main__":
    main()
    # cProfile.run('main()')
