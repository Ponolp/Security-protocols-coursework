from spade import SPADE
import config
import utils
import os
import logging
from Crypto.PublicKey import RSA
import time

class Curator:
    def __init__(self):
        self.q = config.MODULUS
        self.g = config.GENERATOR
        self.sks = []  # Secret keys
        self.pks = []  # Public keys
        self.setup_time = 0
        self.setup_memory = 0
        self.reg_keys = []  # Registration keys !!! IN DATABASE
        self.ciphertexts = []  # Encrypted data !!! IN DATABASE
        self.spade = SPADE(self.q, self.g, config.MAX_PT_VEC_SIZE)
        self.num_users = config.NumUsers
        self.generate_keys()

    def generate_keys(self):
        """
        Generates public and secret keys using SPADE.
        """
        # Generate public and private keys
        self.sks, self.pks, self.setup_time, self.setup_memory = self.spade.setup()
        
        # Generate registration keys (can be random or based on some logic)
        # self.reg_keys = [utils.random_element_in_zmod(self.q) for _ in range(self.num_users)]

    def get_public_params(self):
        """
        Returns the public parameters (q, g) and the public keys (mpk) as bytes.
        """
        q_bytes = self.q.to_bytes((self.q.bit_length() + 7) // 8, byteorder='big')
        g_bytes = self.g.to_bytes((self.g.bit_length() + 7) // 8, byteorder='big')

        mpk_bytes = [pk.to_bytes((pk.bit_length() + 7) // 8, byteorder='big') for pk in self.pks]

        return {
            "q": q_bytes.hex(),
            "g": g_bytes.hex(),
            "mpk": [pk.hex() for pk in mpk_bytes]
        }

    def generate_registration_key(self, user_id):
        """
        Generates a registration key for the user based on user_id.
        """
        return self.reg_keys[user_id]

    def store_encrypted_data(self, user_id, ciphertext):
        """
        Stores encrypted user data (ciphertext).
        """
        if len(self.ciphertexts) <= user_id:
            self.ciphertexts.extend([None] * (user_id - len(self.ciphertexts) + 1))
        self.ciphertexts[user_id] = ciphertext

    def get_encrypted_data(self, user_id):
        """
        Retrieves encrypted data for a specific user.
        """
        if user_id < len(self.ciphertexts):
            return self.ciphertexts[user_id]
        return None
