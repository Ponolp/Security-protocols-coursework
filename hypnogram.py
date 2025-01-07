import random
import requests
import string
import time
import json
import utils
from config import MAX_PT_VEC_SIZE, NumUsers

# Define constants for the API endpoint
BASE_URL_ENCRYPT = "http://localhost:5000/hypnogram/register"
BASE_URL_QUERY = "http://localhost:5000/analyst/query_hypno"
HYPNO_DIR = './datasets/hypnogram'

# Function to generate random DNA sequences
def generate_random_hypno_sequence():
    # Create a list of numbers from 1 to 10
    numbers = list(range(1, 11))
    # Choose a random number from the list
    random_number = random.choice(numbers)
    return random_number

def test_insert_userdata_hypno(user_id, data, vector_size):
    payload = {
        'user_id': user_id,
        'data': data
    }

    headers = {
        'Content-Type': 'application/json'
    }

    start_time = time.time()
    response = requests.post(BASE_URL_ENCRYPT, headers=headers, json=payload)
    elapsed_time = time.time() - start_time
    responseJson = response.json()
    
    # Check if the request was successful
    if response.status_code == 200:
        time_of_reg = responseJson.get('time_of_reg')
        time_of_enc = responseJson.get('time_of_enc')
        peak_memory_reg = responseJson.get('peak_memory_reg')
        peak_memory_enc = responseJson.get('peak_memory_enc')
        print(f"User {user_id} | Vector Size: {vector_size} | Time Taken: {elapsed_time:.4f}s | Time of reg: {time_of_reg:.10f}s | Time of enc: {time_of_enc:.10f}s")
        return elapsed_time, time_of_reg, time_of_enc, peak_memory_reg, peak_memory_enc
    else:
        print(f"Failed request for User {user_id} | Vector Size: {vector_size} | Status Code: {response.status_code} | Error: {responseJson.get('message')}")
        return elapsed_time

# Function to simulate a POST request to the DNA endpoint
def test_query_hypno(user_id, query_value, vector_size):
    payload = {
        'user_id': user_id,
        'query_value': query_value
    }

    headers = {
        'Content-Type': 'application/json'
    }

    start_time = time.time()
    response = requests.post(BASE_URL_QUERY, headers=headers, json=payload)
    elapsed_time = time.time() - start_time
    responseJson = response.json()

    # Check if the request was successful
    if response.status_code == 200:
        time_of_kd = responseJson.get('time_of_kd')
        time_of_dec = responseJson.get('time_of_dec')
        peak_memory_kd = responseJson.get('peak_memory_kd')
        peak_memory_dec = responseJson.get('peak_memory_dec')
        print(f"User {user_id} | Query: {query_value} | Vector Size: {vector_size} | Time Taken: {elapsed_time:.4f}s | Time of kd: {time_of_kd:.10f}s | Time of dec: {time_of_dec:.10f}s")
        return elapsed_time, time_of_kd, time_of_dec, peak_memory_kd, peak_memory_dec
    else:
        print(f"Failed request for User {user_id} | Query: {query_value} | Status Code: {response.status_code} | Error: {responseJson.get('message')}")
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
        elapsed_time, time_of_kd, time_of_dec, peak_memory_kd, peak_memory_dec = test_query_hypno(user, query_value, vector_size)
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

if __name__ == '__main__':
    run_performance_tests()