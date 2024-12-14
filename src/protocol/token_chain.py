import dataclasses as dto
import collections
from src.poly import PolyVec
from src.protocol.pk import AESCyphertext


@dto.dataclass
class OpenToken:
    m: PolyVec
    b: PolyVec
    b2: PolyVec
    s: PolyVec


@dto.dataclass
class ClosedToken:
    m: PolyVec
    b: PolyVec
    c: AESCyphertext

    def open(self, key: int) -> OpenToken:
        b2, s = self.c.decrypt(key=key)
        return OpenToken(self.m, self.b, b2, s)


@dto.dataclass
class TokenChain:
    head: OpenToken
    rest: collections.deque[ClosedToken]
