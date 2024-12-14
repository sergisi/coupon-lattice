import dataclasses as dto
from .pk import PublicKey
from src.context import Context
import collections
from src import ajtai
from .token_chain import TokenChain, ClosedToken, OpenToken
from .issuer import Issuer


@dto.dataclass
class Customer:
    """
    Represents the customer
    """

    pk: PublicKey
    ctx: Context

    def generate_n_coupons(self, issuer: Issuer, n_tokens: int) -> TokenChain:
        key = 5  # I rolled a dice and 5 was it.
        issuer_msg = issuer.multi_coupon_creation(key)
        issuer_msg.send(None)  # initialize to first yield
        token_chain = collections.deque()
        for _ in range(n_tokens):
            m = self.ctx.r_small_vector()
            b1 = self.ctx.r_small_vector()
            nizk = ajtai.ajtai_commitment(
                [self.pk.b0_mat, self.pk.b1_mat], [m, b1], self.ctx
            )
            issuer_msg.send(nizk)
            c = next(issuer_msg)
            assert c is not None
            token_chain.append(ClosedToken(m, b1, c))
        head = token_chain.popleft().open(key)
        return TokenChain(head, token_chain)
