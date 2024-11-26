"""
Module that has the protocol described on the article 
	`Quantum-resistant asymmetric blind computation with
	applications to priced oblivious transfer`

The protocol is described as the function protocol(), and 
has some helper functions, mainly to derive stats from 
the protocol or some security.

It has some helper functions to collect more than one execution, 
skimming all the times that the protocol has been correct.
"""

from src.count import bob_count, alice_count, transmission_count
from src.context import get_context
import cProfile
from protocol import protocol, p_is_correct


def profile_protocol():
    cProfile.run("protocol()")
    print("\n\n\n\n\n\n\n")
    print("Study of number of elements")
    print(f"Bob count {bob_count}")
    print(f"Alice count {alice_count}")
    print(f"Transmission count {transmission_count}")


if __name__ == "__main__":
    ctx = get_context()
    assert p_is_correct(ctx)
