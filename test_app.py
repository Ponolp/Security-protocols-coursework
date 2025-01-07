import atexit
from models.handlers import DBHandler, PBHandler
from models.user import User, create_user
from models.curator import Curator
from spade import SPADE
from config import DbName, TbName, NumUsers, PaddingItem, MODULUS, GENERATOR, MAX_PT_VEC_SIZE
from utils import read_dna_seq_file, convert_dna_seq_to_dinucleotide, map_dinucleotide_to_int, add_padding
import json
import os
import time
import tracemalloc
import random
import utils

# Initialize database handler
db_handler = DBHandler(DbName, TbName)

# Create table if it doesn't exist
db_handler.create_users_cipher_table()


# Directory containing the DNA files
DNA_DIR = './datasets/dna/'
HYPNO_DIR = './datasets/hypnogram'
    
def register_hypnogram(user_id, dataset):
    start_time = time.time()
    try:

        # Initialize the user
        user, time_of_reg, time_of_enc, current_reg, peak_memory_reg, current_enc, peak_memory_enc = create_user(user_id, dataset, MAX_PT_VEC_SIZE, curator)

        # Time taken
        elapsed_time = time.time() - start_time
        print(f"User finished in {elapsed_time:.10f} seconds")

        return json.dumps({
            "status": "success",
            "message": "User registered and hypnogram data encrypted successfully!",
            "time_of_reg": time_of_reg,
            "time_of_enc": time_of_enc,
            "current_reg": current_reg,
            "peak_memory_reg": peak_memory_reg,
            "current_enc": current_enc,
            "peak_memory_enc": peak_memory_enc
        }), 200

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}), 500
    

def register_dna(user_id, dna_data):
    start_time = time.time()
    try:   

        # Initialize the user
        user, time_of_reg, time_of_enc, current_reg, peak_memory_reg, current_enc, peak_memory_enc = create_user(user_id, dna_data, MAX_PT_VEC_SIZE, curator)
       
        elapsed_time = time.time() - start_time
        print(f"User finished in {elapsed_time:.10f} seconds")
        dbSize = os.path.getsize(DbName)
        print(f"Database size: {dbSize / (1024 * 1024):.2f} MB")  # Convert to MB
        return json.dumps({
            "status": "success", 
            "message": "DNA data registered successfully!",
            "time_of_reg": time_of_reg,
            "time_of_enc": time_of_enc,
            "current_reg": current_reg,
            "peak_memory_reg": peak_memory_reg,
            "current_enc": current_enc,
            "peak_memory_enc": peak_memory_enc
        }), 200

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}), 500


def analyst_query(user_id, query_value):
    start_time = time.time()
    try:

        db_handler2 = DBHandler(DbName, TbName)

        # Retrieve user data from the database
        user_req = db_handler2.get_user_req_by_id(user_id)
        if not user_req:
            return json.dumps({"status": "error", "message": "User data not found!"}), 404

        db_handler2.close_connection()

        # Start the analyst operation (decrypt the user's data)
        spade = SPADE(MODULUS, GENERATOR, MAX_PT_VEC_SIZE)
        

        # Derive decryption keys using the provided query value and the registration key
        reg_key = int.from_bytes(user_req['reg_key'], byteorder='big')
        tracemalloc.start()
        start_time = time.time()
        dk = spade.key_derivation(user_id, query_value, curator.sks, reg_key)
        time_of_kd = time.time() - start_time
        current_kd, peak_memory_kd = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Decrypt the ciphertext using the derived keys
        ciphertext = user_req['ciphertext']
        # Reconstruct ciphertext from stored bytes
        reconstructed_ciphertext = []
        for c0_bytes, c1_bytes in ciphertext:  # Assume storage preserves tuple structure
            c0 = int.from_bytes(c0_bytes, byteorder='big')
            c1 = int.from_bytes(c1_bytes, byteorder='big')
            reconstructed_ciphertext.append([c0, c1])  # Restore as [c0, c1] pairs

        tracemalloc.start()
        start_time = time.time()
        decrypted = spade.decrypt(dk, query_value, reconstructed_ciphertext)
        time_of_decrypt = time.time() - start_time
        current_dec, peak_memory_dec = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Time taken
        elapsed_time = time.time() - start_time
        print(f"Query finished in {elapsed_time:.10f} seconds")

        # Respond with the decrypted result
        return json.dumps({
            "status": "success",
            "query_value": query_value,
            "decrypted_result": decrypted,  # Return the decrypted result
            "time_of_kd": time_of_kd,
            "time_of_dec": time_of_decrypt,
            "current_kd": current_kd,
            "peak_memory_kd": peak_memory_kd,
            "current_dec": current_dec,
            "peak_memory_dec": peak_memory_dec
        }), 200

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}), 500
    
def analyst_query_dna(user_id, query_value_str):
    start_time = time.time()
    try:

        # Map dinucleotide to integer (e.g., "CC" -> 6)
        query_value = map_dinucleotide_to_int([query_value_str])[0]

        db_handler2 = DBHandler(DbName, TbName)

        # Retrieve user data from the database
        user_req = db_handler2.get_user_req_by_id(user_id)
        if not user_req:
            return json.dumps({"status": "error", "message": "User data not found!"}), 404

        db_handler2.close_connection()

        # Start the analyst operation (decrypt the user's data)
        spade = SPADE(MODULUS, GENERATOR, MAX_PT_VEC_SIZE)
        
        tracemalloc.start()
        start_time = time.time()
        # Derive decryption keys using the provided query value and the registration key
        reg_key = int.from_bytes(user_req['reg_key'], byteorder='big')
        dk = spade.key_derivation(user_id, query_value, curator.sks, reg_key)
        time_of_kd = time.time() - start_time
        current_kd, peak_memory_kd = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Decrypt the ciphertext using the derived keys
        ciphertext = user_req['ciphertext']
        # Reconstruct ciphertext from stored bytes
        reconstructed_ciphertext = []
        for c0_bytes, c1_bytes in ciphertext:  # Assume storage preserves tuple structure
            c0 = int.from_bytes(c0_bytes, byteorder='big')
            c1 = int.from_bytes(c1_bytes, byteorder='big')
            reconstructed_ciphertext.append([c0, c1])  # Restore as [c0, c1] pairs

        tracemalloc.start()
        start_time = time.time()
        decrypted = spade.decrypt(dk, query_value, reconstructed_ciphertext)
        time_of_decrypt = time.time() - start_time
        current_dec, peak_memory_dec = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Time taken
        elapsed_time = time.time() - start_time
        print(f"Query finished in {elapsed_time:.10f} seconds")

        # Respond with the decrypted result
        return json.dumps({
            "status": "success",
            "query_value": query_value,
            "decrypted_result": decrypted,
            "time_of_kd": time_of_kd,
            "time_of_dec": time_of_decrypt,
            "current_kd": current_kd,
            "peak_memory_kd": peak_memory_kd,
            "current_dec": current_dec,
            "peak_memory_dec": peak_memory_dec
        }), 200

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}), 500

# Function to generate random DNA sequences
def generate_random_hypno_sequence():
    # Create a list of numbers from 1 to 10
    numbers = list(range(1, 11))
    # Choose a random number from the list
    random_number = random.choice(numbers)
    return random_number

def test_insert_userdata_hypno(user_id, data, vector_size):

    start_time = time.time()
    response = register_hypnogram(user_id, data)
    elapsed_time = time.time() - start_time
    responseJson = json.loads(response[0])
    print(responseJson)
    # Check if the request was successful
    if response[1] == 200:
        time_of_reg = responseJson.get('time_of_reg')
        time_of_enc = responseJson.get('time_of_enc')
        peak_memory_reg = responseJson.get('peak_memory_reg')
        peak_memory_enc = responseJson.get('peak_memory_enc')
        print(f"User {user_id} | Vector Size: {vector_size} | Time Taken: {elapsed_time:.4f}s | Time of reg: {time_of_reg:.10f}s | Time of enc: {time_of_enc:.10f}s")
        return elapsed_time, time_of_reg, time_of_enc, peak_memory_reg, peak_memory_enc
    else:
        print(f"Failed request for User {user_id} | Vector Size: {vector_size} | Status Code: {response[1]} | Error: {responseJson.get('message')}")
        return elapsed_time

# Function to simulate a POST request to the DNA endpoint
def test_query_hypno(user_id, query_value, vector_size):

    start_time = time.time()
    response = analyst_query(user_id, query_value)
    elapsed_time = time.time() - start_time
    responseJson = json.loads(response[0])

    # Check if the request was successful
    if response[1] == 200:
        time_of_kd = responseJson.get('time_of_kd')
        time_of_dec = responseJson.get('time_of_dec')
        peak_memory_kd = responseJson.get('peak_memory_kd')
        peak_memory_dec = responseJson.get('peak_memory_dec')
        print(f"User {user_id} | Query: {query_value} | Vector Size: {vector_size} | Time Taken: {elapsed_time:.4f}s | Time of kd: {time_of_kd:.10f}s | Time of dec: {time_of_dec:.10f}s")
        return elapsed_time, time_of_kd, time_of_dec, peak_memory_kd, peak_memory_dec
    else:
        print(f"Failed request for User {user_id} | Query: {query_value} | Status Code: {response[1]} | Error: {responseJson.get('message')}")
        return elapsed_time

# Function to generate and test multiple users with different vector sizes
def run_performance_tests():
    user_count = NumUsers
    vector_size = MAX_PT_VEC_SIZE
    
    # Process all hypnogram files in the directory
    hypnogram_data = utils.process_hypnogram_files(HYPNO_DIR)
    
    query_value = generate_random_hypno_sequence()

    print(f"Running encrypt test with {user_count} users and vector size {vector_size}...")
    total_time1 = 0
    total_reg_time = 0
    total_enc_time = 0
    total_memory_reg = 0
    total_memory_enc = 0
    for i, dataset in zip(range(user_count), hypnogram_data):
        # Simulate the request
        elapsed_time, time_of_reg, time_of_enc, peak_memory_reg, peak_memory_enc = test_insert_userdata_hypno(i, dataset, vector_size)
        total_time1 += elapsed_time
        total_reg_time += time_of_reg
        total_enc_time += time_of_enc
        total_memory_reg += peak_memory_reg
        total_memory_enc += peak_memory_enc
            
    average_time = total_time1 / user_count
    print(f"Average response time for {user_count} users with vector size {vector_size}: {average_time:.4f}s")
    print(f"Total registration time for {user_count} users: {total_reg_time:.10f}s")
    print(f"Total encryption time for {user_count} users: {total_enc_time:.10f}s")
    print(f"Total memory allecations for registration: {total_memory_reg / 1024:.2f} KB")
    print(f"Total memory allecations for encryption: {total_memory_enc / 1024:.2f} KB\n")

    total_time2 = 0
    total_kd_time = 0
    total_dec_time = 0
    total_memory_kd = 0
    total_memory_dec = 0
    for user in range(user_count):
        # Simulate the request
        response = test_query_hypno(user, query_value, vector_size)
        if len(response) > 1:
            elapsed_time = response[0] 
            time_of_kd = response[1] 
            time_of_dec = response[2] 
            peak_memory_kd = response[3] 
            peak_memory_dec = response[4]
            total_time2 += elapsed_time
            total_kd_time += time_of_kd
            total_dec_time += time_of_dec
            total_memory_kd += peak_memory_kd
            total_memory_dec += peak_memory_dec

    average_time = total_time2 / user_count
    print(f"Average response time for {user_count} users with vector size {vector_size}: {average_time:.4f}s")
    print(f"Total key derivation time for {user_count} users: {total_kd_time:.10f}s")
    print(f"Total decryption time for {user_count} users: {total_dec_time:.10f}s")
    print(f"Total memory allecations for key derivation: {total_memory_kd / 1024:.2f} KB")
    print(f"Total memory allecations for decryption: {total_memory_dec / 1024:.2f} KB\n")

def cleanup():
    """Close the database connection and remove the database file when the program exits."""
    try:
        # Ensure the database connection is closed
        db_handler.close_connection()  # Ensure DBHandler has a close_connection() method
        print("Database connection closed.")

        # Remove the database file
        if os.path.exists(DbName):
            os.remove(DbName)
            print(f"Database {DbName} has been removed.")
    except Exception as e:
        print(f"Error during cleanup: {e}")


if __name__ == '__main__':
    curator = Curator()
    print(f"Setup time: {curator.setup_time}s")
    print(f"Setup memory allecation: {curator.setup_memory / 1024:.2f} KB")

    run_performance_tests()


    # Register the cleanup function to execute at program exit
    atexit.register(cleanup)

