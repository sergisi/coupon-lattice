import unittest

from src.ajtai import ajtai_commitment
from src.context import gotta_go_fast_context


class AjtaiTest(unittest.TestCase):

    def setUp(self) -> None:
        self.ctx = gotta_go_fast_context()
        return super().setUp()

    def test_ajtai(self):
        matrices = [self.ctx.random_vector() for _ in range(2)]
        vectors = [self.ctx.r_small_vector() for _ in range(2)]
        commitment = ajtai_commitment(matrices, vectors, self.ctx)
        self.assertTrue(commitment())
