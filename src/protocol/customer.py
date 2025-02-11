import dataclasses as dto
from .pk import PublicKey
from src.context import Context
import collections
from src import ajtai
from .token_chain import TokenChain, ClosedToken, OpenToken
from .issuer import Issuer
import secrets


@dto.dataclass
class Customer:
    """
    Represents the customer
    """

    pk: PublicKey
    ctx: Context

    def generate_n_coupons(
        self, issuer: Issuer, n_tokens: int, initial_key: int | None = None
    ) -> TokenChain:
        if initial_key is None:
            key = secrets.randbits(256)
        else:
            key = initial_key
        issuer_msg = issuer.multi_coupon_creation(key)
        issuer_msg.send(None)  # initialize to first yield
        token_chain = collections.deque()
        for _ in range(n_tokens):
            m = self.ctx.r_small_vector()
            b1 = self.ctx.r_small_vector()
            nizk = ajtai.ajtai_commitment(
                [self.pk.b0_mat, self.pk.b1_mat], [m, b1], self.ctx
            )
            c, mask = issuer_msg.send(nizk)
            token_chain.append(ClosedToken(m, b1, c, mask))
        head = token_chain.popleft().open(key)
        return TokenChain(head, token_chain)

    def redeem_token(
        self, issuer: Issuer, token_chain: TokenChain
    ) -> TokenChain | None:
        nizk = ajtai.ajtai_commitment(
            [self.pk.a_mat, self.pk.b1_mat, self.pk.b2_mat],
            [token_chain.head.s, -token_chain.head.b, -token_chain.head.b2],
            self.ctx,
        )
        r = issuer.redeem_token(nizk, token_chain.head.m)
        # Use message to perform whatever with the merchant
        if len(token_chain) < 2:
            return None
        expected = r + self.pk.r * token_chain.head.b
        mask = token_chain.head.mask
        partial_key = self.ctx.apply_mask(self.ctx.collapse(expected), mask)
        next_key = hash((token_chain.head.key, partial_key))
        return token_chain.open(next_key)
