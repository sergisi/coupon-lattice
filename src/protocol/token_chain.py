import collections
from collections.abc import Sized
import dataclasses as dto

import typing
from src.poly import PolyVec
from src.protocol.pk import AESCyphertext


@dto.dataclass
class OpenToken:
    m: PolyVec
    b: PolyVec
    b2: PolyVec
    s: PolyVec
    mask: list[int]
    key: int


@dto.dataclass
class ClosedToken:
    m: PolyVec
    b: PolyVec
    c: AESCyphertext
    mask: list[int]

    def open(self, key: int) -> OpenToken:
        b2, s = self.c.decrypt(key=key)
        return OpenToken(self.m, self.b, b2, s, self.mask, key)


@dto.dataclass
class TokenChain(Sized):
    head: OpenToken
    rest: collections.deque[ClosedToken]

    def open(self, key: int) -> typing.Self:
        """
        Mutable method that sets new open token head.
        """
        self.head = self.rest.popleft().open(key)
        return self

    def __len__(self) -> int:
        return 1 + len(self.rest)
