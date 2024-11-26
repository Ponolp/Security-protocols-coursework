def enc(mpk, x, alpha, g, q):
    """
    Encrypts data using the master public key (mpk), the user's private key (alpha),
    the group generator (g), and modulus (q).

    Args:
        mpk (list): Master public key components (list of group elements).
        x (list): Message vector to encrypt.
        alpha (int): User's private key component.
        g (int): Generator of the cyclic group.
        q (int): Order of the cyclic group.

    Returns:
        tuple: A tuple containing two lists:
            h (list): Helping information for decryption.
            c (list): Encrypted data.
    """
    import random
    
    S = range(1, q, 2)  # Subset of odd integers in Zq (odd numbers modulo q)
    r = [random.choice(S) for _ in x]  # Generate random noise values for each entry in x
    
    # Encryption process
    h = [pow(g, alpha + ri, q) for ri in r]  # Helping information
    c = [(pow(mpk[i], alpha * xi, q) * pow(g, ri, q)) % q for i, (xi, ri) in enumerate(zip(x, r))]  # Ciphertext
    
    return h, c

