"""
The protocol class and some helpful funtcions.

The protocol is made by three actors.
- The issuer
- The merchant
- The customer

Actually, the merchant is only needed for the payment of the classes, so
it does not make any sense to implement it.
"""

import dataclasses as dto

from src import falcon
from src.context import Context
from .issuer import Issuer
from .customer import Customer
from .pk import PublicKey, aes, AESCyphertext


__all__ = [
    "Issuer",
    "Customer",
    "PublicKey",
    "aes",
    "AESCyphertext",
    "Protocol",
    "set_up",
]


@dto.dataclass
class Protocol:
    """ """

    issuer: Issuer
    customer: Customer
    ctx: Context


def set_up(ctx: Context) -> Protocol:
    """
    Sets up the relevant actors and their keys.
    """
    falc = falcon.MyFalcon(ctx)
    x = ctx.r_small()
    b1_mat = ctx.random_vector()
    r = x * b1_mat + ctx.r_small_vector()
    pk = PublicKey(
        a_mat=falc.A,
        b0_mat=ctx.random_vector(),
        b1_mat=b1_mat,
        b2_mat=ctx.random_vector(),
        r=r,
    )
    issuer = Issuer(pk, falc, x, ctx)
    customer = Customer(pk, ctx)
    return Protocol(issuer, customer, ctx)
