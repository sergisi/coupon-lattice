import unittest
from src import ajtai
from src.protocol import AESCyphertext, set_up, Issuer, Customer, Protocol
from src.context import Context, get_context, gotta_go_fast_context


class TestProtocolFast(unittest.TestCase):
    ctx: Context
    protocol: Protocol
    issuer: Issuer
    customer: Customer

    def setUp(self) -> None:
        self.ctx = gotta_go_fast_context()
        self.protocol = set_up(self.ctx)
        self.issuer = self.protocol.issuer
        self.customer = self.protocol.customer
        return super().setUp()

    def test_correct_generation_of_coupons(self):
        issuer_msg = self.issuer.multi_coupon_creation(key=5)
        key = 5
        issuer_msg.send(None)  # initialize coroutine
        for _ in range(5):
            m = self.ctx.r_small_vector()
            b1 = self.ctx.r_small_vector()
            nizk = ajtai.ajtai_commitment(
                [self.customer.pk.b0_mat, self.customer.pk.b1_mat], [m, b1], self.ctx
            )
            self.assertTrue(nizk())
            msg = issuer_msg.send(nizk)
            self.assertNotEqual(None, msg)
            c, mask = msg
            self.assertEqual(c.key, key)
            partial_key = self.ctx.apply_mask(
                self.ctx.collapse(self.issuer.x * nizk.t), mask
            )
            key = hash((key, partial_key))


@unittest.skip("Its really slow, and TestProtocolFast should be ok.")
class TestProtocolSlow(unittest.TestCase):
    ctx: Context
    protocol: Protocol
    issuer: Issuer
    customer: Customer

    def setUp(self) -> None:
        self.ctx = get_context()
        self.protocol = set_up(self.ctx)
        self.issuer = self.protocol.issuer
        self.customer = self.protocol.customer
        return super().setUp()

    def test_correct_generation_of_coupons(self):
        issuer_msg = self.issuer.multi_coupon_creation(key=5)
        key = 5
        issuer_msg.send(None)  # initialize coroutine
        for _ in range(5):
            m = self.ctx.r_small_vector()
            b1 = self.ctx.r_small_vector()
            nizk = ajtai.ajtai_commitment(
                [self.customer.pk.b0_mat, self.customer.pk.b1_mat], [m, b1], self.ctx
            )
            self.assertTrue(nizk())
            msg = issuer_msg.send(nizk)
            self.assertNotEqual(None, msg)
            c, mask = msg
            self.assertEqual(c.key, key)
            partial_key = self.ctx.apply_mask(
                self.ctx.collapse(self.issuer.x * nizk.t), mask
            )
            key = hash((key, partial_key))
