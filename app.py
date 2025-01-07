from flask import Flask, request, jsonify
import atexit
from models.handlers import DBHandler
from models.user import User, create_user
from models.curator import Curator
from spade import SPADE
from config import DbName, TbName, MODULUS, GENERATOR, MAX_PT_VEC_SIZE
from utils import map_dinucleotide_to_int
import os
import time
import tracemalloc

app = Flask(__name__)

# Initialize database handler
db_handler = DBHandler(DbName, TbName)

# Create table if it doesn't exist
db_handler.create_users_cipher_table()


# Directory containing the DNA files
DNA_DIR = './datasets/dna/'
HYPNO_DIR = './datasets/hypnogram'
    
@app.route('/hypnogram/register', methods=['POST'])
def register_hypnogram():
    start_time = time.time()
    try:
        # Get user data from request
        data = request.get_json()
        user_id = data['user_id']
        dataset = data['data']

        # Initialize the user
        user, time_of_reg, time_of_enc, current_reg, peak_memory_reg, current_enc, peak_memory_enc = create_user(user_id, dataset, MAX_PT_VEC_SIZE, curator)

        # Time taken
        elapsed_time = time.time() - start_time
        print(f"User finished in {elapsed_time:.10f} seconds")

        return jsonify({
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
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/dna/register', methods=['POST'])
def register_dna():
    start_time = time.time()
    try:
        # Get user data from request
        data = request.get_json()
        user_id = data['user_id']
        dna_data = data['data']       

        # Initialize the user
        user, time_of_reg, time_of_enc, current_reg, peak_memory_reg, current_enc, peak_memory_enc = create_user(user_id, dna_data, MAX_PT_VEC_SIZE, curator)
       
        elapsed_time = time.time() - start_time
        print(f"User finished in {elapsed_time:.10f} seconds")
        dbSize = os.path.getsize(DbName)
        print(f"Database size: {dbSize / (1024 * 1024):.2f} MB")  # Convert to MB
        return jsonify({
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
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/analyst/query_hypno', methods=['POST'])
def analyst_query():
    start_time = time.time()
    try:
        # Get analyst data from request
        data = request.get_json()
        user_id = data['user_id']
        query_value = data['query_value']

        db_handler2 = DBHandler(DbName, TbName)

        # Retrieve user data from the database
        user_req = db_handler2.get_user_req_by_id(user_id)
        if not user_req:
            return jsonify({"status": "error", "message": "User data not found!"}), 404

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
        return jsonify({
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
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/analyst/query_dna', methods=['POST'])
def analyst_query_dna():
    start_time = time.time()
    try:
        # Get analyst data from request
        data = request.get_json()
        user_id = data['user_id']
        query_value_str = data['query_value']  # This will be a string like "CC"

        # Map dinucleotide to integer (e.g., "CC" -> 6)
        query_value = map_dinucleotide_to_int([query_value_str])[0]

        db_handler2 = DBHandler(DbName, TbName)

        # Retrieve user data from the database
        user_req = db_handler2.get_user_req_by_id(user_id)
        if not user_req:
            return jsonify({"status": "error", "message": "User data not found!"}), 404

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

        # Reconstruct ciphertext from stored bytes
        ciphertext = user_req['ciphertext']        
        reconstructed_ciphertext = []
        for c0_bytes, c1_bytes in ciphertext:  # Assume storage preserves tuple structure
            c0 = int.from_bytes(c0_bytes, byteorder='big')
            c1 = int.from_bytes(c1_bytes, byteorder='big')
            reconstructed_ciphertext.append([c0, c1])  # Restore as [c0, c1] pairs

        # Decrypt the ciphertext using the derived keys
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
        return jsonify({
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
        return jsonify({"status": "error", "message": str(e)}), 500

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

    # Register the cleanup function to execute at program exit
    atexit.register(cleanup)

    app.run(host='0.0.0.0', port=5000, debug=True)
