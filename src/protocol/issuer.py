import dataclasses as dto
import typing
from src import falcon
from src.poly import Poly, PolyVec
from .pk import PublicKey, aes, AESCyphertext
from src.context import Context
from src.ajtai import AjtaiCommitment


@dto.dataclass
class Issuer:
    """
    Represents the issuer in the protocol.
    """

    pk: PublicKey
    falcon: falcon.MyFalcon
    x: Poly
    ctx: Context
    issued_before: set[PolyVec] = dto.field(default_factory=set)

    def multi_coupon_creation(
        self, key: int
    ) -> typing.Generator[tuple[AESCyphertext, list[int]], AjtaiCommitment, None]:
        # It gets whacky in the client if not.
        msg: AjtaiCommitment | None = yield
        while True:
            assert msg is not None
            assert msg(), "pi_t not generated correctly!"
            expected = self.x * msg.t
            mask = self.ctx.get_mask_of_element(expected)
            partial_key = self.ctx.apply_mask(self.ctx.collapse(expected), mask)
            next_key = hash((key, partial_key))
            print(f"NextKey = {(key, partial_key)}")
            b3 = self.ctx.r_small_vector()
            s = self.falcon.my_sign(msg.t + self.pk.b2_mat * b3)
            c = aes(b3, s, key=key)
            key = next_key
            msg = yield c, mask

    def redeem_token(self, nizk: AjtaiCommitment, m: PolyVec) -> Poly:
        assert nizk(), "nizk not generated correctly"
        assert self.pk.b0_mat * m == nizk.t
        assert m not in self.issued_before
        self.issued_before.add(m)
        # Informs the merchant so that they can perform whatever
        return self.x * self.pk.b0_mat * m + self.ctx.r_small()
