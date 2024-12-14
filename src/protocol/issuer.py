import dataclasses as dto
import typing
from src import falcon
from src.poly import Poly
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

    def multi_coupon_creation(
        self, key: int
    ) -> typing.Generator[
        tuple[AESCyphertext, list[int]] | None, AjtaiCommitment | None, None
    ]:
        msg: AjtaiCommitment | None = yield
        while True:
            assert msg is not None
            assert msg(), "pi_t not generated correctly!"
            expected = self.x * msg.t
            mask = self.ctx.get_mask_of_element(expected)
            partial_key = self.ctx.apply_mask(self.ctx.collapse(expected), mask)
            next_key = hash((key, partial_key))
            b3 = self.ctx.r_small_vector()
            s = self.falcon.my_sign(msg.t + self.pk.b2_mat * b3)
            c = aes(b3, s, key=key)
            key = next_key
            msg = yield c, mask
