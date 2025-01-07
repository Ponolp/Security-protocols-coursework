import time
from random import randint
import utils  
from spade import SPADE
from config import DbName, TbName  # Import from config
from models.handlers import DBHandler, PBHandler
import tracemalloc

# Assuming the User class remains similar, managing user state
class User:
    def __init__(self, uid, q, g, mpk):
        self.id = uid
        self.q = q
        self.g = g
        self.alpha = None
        self.mpk = mpk

    @staticmethod
    def new_user(uid, q, g, mpk):
        return User(uid, q, g, mpk)

def create_user(user_id, data, max_vec_size, curator):

    db_handler = DBHandler(DbName, TbName)
    pb_handler = PBHandler()

    # Fetch public parameters from the Curator
    public_params_resp = pb_handler.read_public_params(curator.get_public_params())

    q, g, mpk = public_params_resp  # Extract modulus (q), generator (g), and mpk

    # Initialize user
    user = User(user_id, q, g, mpk)

    # Initialize SPADE
    spade_instance = SPADE(q, g, max_vec_size)  # Pass correct parameters

    tracemalloc.start()
    start_time = time.time()
    # Generate random secret for the user
    user.alpha = randint(1, q - 1)
    reg_key = spade_instance.register(user.alpha)
    time_of_reg = time.time() - start_time
    current_reg, peak_memory_reg = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    tracemalloc.start()
    start_time = time.time()
    # Encrypt user's data using "mpk" (public key)
    ciphertext = spade_instance.encrypt(mpk, user.alpha, data)
    time_of_enc = time.time() - start_time
    current_enc, peak_memory_enc = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Flatten ciphertext for transmission
    ciphertext_bytes = []
    for c0, c1 in ciphertext:  # Each row is [c0, c1]
        c0_bytes = c0.to_bytes((c0.bit_length() + 7) // 8, byteorder='big')
        c1_bytes = c1.to_bytes((c1.bit_length() + 7) // 8, byteorder='big')
        ciphertext_bytes.append((c0_bytes, c1_bytes))  # Store as tuples


    # Prepare the data to be sent (including the ciphertext and reg_key)
    enc_data = {
        'id': user.id,
        'regKey': reg_key.to_bytes((reg_key.bit_length() + 7) // 8, byteorder='big'),
        'ciphertext': ciphertext_bytes,
    }
 
    db_handler.insert_users_cipher(enc_data)
    db_handler.close_connection()

    return user, time_of_reg ,time_of_enc, current_reg, peak_memory_reg, current_enc, peak_memory_enc




