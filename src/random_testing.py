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

msk, mpk = setup(n, q, g)
print("Master Secret Key (msk):", msk)
print("Master Public Key (mpk):", mpk)

# Encryption
def enc(mpk, x, alpha_j, g, q):
    r = [random.choice(S) for _ in range(len(x))]  # Noise sampled from S
    h = [generate_group_elements(g, alpha_j + ri, q) for ri in r]
    c = [generate_group_elements(g, alpha_j * si + ri * xi, q) 
         for si, ri, xi in zip(mpk, r, x)]
    return h, c

# Example usage
x = [random.randint(1, t) for _ in range(n)]  # Message
alpha_j = random.randint(1, q - 1)  # User's secret key
h, c = enc(mpk, x, alpha_j, g, q)
print("Encryption (h):", h)
print("Encryption (c):", c)


# Key generation
def key_der(msk, v, alpha_j, g, q):
    dk = [generate_group_elements(g, alpha_j * (v - si), q) for si in msk]
    return dk

# Example usage
v = random.randint(1, t)  # Value to check
dk = key_der(msk, v, alpha_j, g, q)
print("Decryption Key (dk):", dk)


# Decryption
def dec(dk, c, h, v, g, q):
    y = []
    for ci, hi, ki in zip(c, h, dk):
        temp = (ci * pow(hi, -v, q) * ki) % q
        y.append(temp)
    return y

# Example usage
y = dec(dk, c, h, v, g, q)
print("Decrypted Results (y):", y)

# Interpretation: y[i] = 1 iff x[i] = v
result = [1 if yi == 1 else 0 for yi in y]
print("Result Vector:", result)
