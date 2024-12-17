import unittest
from src import ajtai
from src.protocol import AESCyphertext, set_up, Issuer, Customer, Protocol
from src.context import Context, get_context, gotta_go_fast_context


class TestProtocolFast(unittest.TestCase):
    ctx: Context
    protocol: Protocol
    issuer: Issuer
    customer: Customer
    tries: int

    def setUp(self) -> None:
        self.ctx = gotta_go_fast_context()
        self.protocol = set_up(self.ctx)
        self.issuer = self.protocol.issuer
        self.customer = self.protocol.customer
        self.tries = 5
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
            expected_partial_key = self.ctx.apply_mask(
                self.ctx.collapse(self.issuer.x * nizk.t), mask
            )
            r = self.issuer.x * self.customer.pk.b0_mat * m + self.ctx.r_small()
            expected = r + self.customer.pk.r * b1
            real_partial_key = self.ctx.apply_mask(self.ctx.collapse(expected), mask)
            self.assertEqual(expected_partial_key, real_partial_key)
            key = hash((key, expected_partial_key))

    def test_customer_and_issuer(self):
        token_chain = self.customer.generate_n_coupons(
            self.issuer, self.tries, initial_key=5
        )
        while token_chain is not None:
            token_chain = self.customer.redeem_token(self.issuer, token_chain)


class TestProtocolSlow(TestProtocolFast):
    ctx: Context
    protocol: Protocol
    issuer: Issuer
    customer: Customer

    def setUp(self) -> None:
        self.ctx = get_context()
        self.protocol = set_up(self.ctx)
        self.issuer = self.protocol.issuer
        self.customer = self.protocol.customer
        self.tries = 100
