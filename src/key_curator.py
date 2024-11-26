def key_der(msk, v, alpha, g, q):
    """Generates decryption key for user-specific value."""
    dk = [pow(g, alpha * (v - si), q) for si in msk]
    return dk
