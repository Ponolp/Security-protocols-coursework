import random
from sympy import isprime, nextprime

# Helper functions
def generate_group_elements(base, exp, modulus):
    return pow(base, exp, modulus)

# Parameters
n = 5  # Number of entries in the message
t = 10  # Range of entries
q = nextprime(2**10)  # Large prime > t + 1
g = 2  # Base of the cyclic group
S = [x for x in range(1, q) if x % 2 == 1]  # Set of odd integers in Z_q

# Setup Algorithm
def setup(n, q, g):
    # Generate master secret key
    msk = [random.randint(1, q - 1) for _ in range(n)]
    # Generate master public key
    mpk = [generate_group_elements(g, si, q) for si in msk]
    return msk, mpk

# msk, mpk = setup(n, q, g)
# print("Master Secret Key (msk):", msk)
# print("Master Public Key (mpk):", mpk)