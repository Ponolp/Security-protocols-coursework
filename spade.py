# spade.py
import random
from sympy import mod_inverse
from utils import gcd, random_element_in_zmod
import tracemalloc
import time

class SPADE:
    def __init__(self, modulus, generator, max_pt_vec_size):
        """
        Initialize SPADE with the modulus (q), generator (g), and the maximum plaintext vector size (n).
        """
        self.n = max_pt_vec_size
        self.q = modulus
        self.g = generator
        
        if gcd(self.g, self.q) != 1:
            raise ValueError("Generator and modulus are not relatively prime!")
    
    def setup(self):
        """
        Setup generates the secret and public keys for SPADE.
        """
        tracemalloc.start()
        start_time = time.time()
        sks = [random_element_in_zmod(self.q) for _ in range(self.n)]
        pks = [pow(self.g, sk, self.q) for sk in sks]
        time_taken = time.time() - start_time
        current, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return sks, pks, time_taken, peak_memory
    
    def register(self, alpha):
        """
        Register the user by generating the registration key.
        """
        return pow(self.g, alpha, self.q)
    
    def encrypt(self, pks, alpha, data):
        """
        Encrypt the data using the public key vector `pks` and the user-specific `alpha`.
        """
        #if len(data) != self.n:
        #    raise ValueError("The input data size doesn't match the expected vector size!")
        
        ciphertext = []
        for i in range(self.n):
            r = random_element_in_zmod(self.q)
         
            # Ensure r is odd
            if r % 2 == 0:
                r += 1
            # c0 = g^(r_i+alpha), the helping information
            c0 = pow(self.g, r + alpha, self.q)
            m = data[i]
            # cI1 = (pk^alpha)*((g^r_i)^m_i)
            c1 = (pow(pks[i], alpha, self.q) * pow(pow(self.g, r, self.q), m, self.q)) % self.q
            ciphertext.append([c0, c1])
        
        return ciphertext
    
    def key_derivation(self, id, value, sks, reg_key):
        """
        Derive the decryption keys for a specific query value `v` and user `id`.
        """
        dk = []
        for i in range(self.n):
            vs = value - sks[i]
            dk.append(pow(reg_key, vs, self.q))
        return dk
    
    def decrypt(self, dk, value, ciphertexts):
        """
        Decrypt the ciphertexts using the decryption keys `dk` and query value `v`.
        """
        results = []
        for i in range(self.n):
            ci = ciphertexts[i]
        
            # vb is the negation of the value (in Python, we handle big integers with the int type)
            vb = -value
        
            # Calculate ci[0] ^ (-value) % q
            # This is equivalent to finding the modular inverse of ci[0] ** value mod q
            c0_inv = pow(ci[0], vb, self.q)
        
            # Now, yi = dk[i] * (ci[1] * c0_inv) % q
            yi = (dk[i] * (ci[1] * c0_inv) % self.q) % self.q
        
            # Append the decrypted value to the results
            results.append(yi)
    
        return results
