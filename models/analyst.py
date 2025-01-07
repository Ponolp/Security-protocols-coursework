import time
import requests
from math import gcd
import utils  # Assuming you still need to use utility functions
from spade import SPADE
from models.handlers import PBHandler
from config import MAX_PT_VEC_SIZE

# Assuming the Analyst class interacts with an external SPADE instance, we can keep this as-is
class Analyst:      
    def __init__(self, name):
        self.name = name

    def query_data(self, user_id, query_value, URL):
        payload = {
        'user_id': user_id,
        'query_value': query_value
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(URL, headers=headers, json=payload)
        responseJson = response.json()
        decrypted_data = responseJson.get('decrypted_result')
        return decrypted_data

    def count_the_value(self, decrypted_data):
        """
        Count the amount of the value (1 since the query values is 1 in the decryption) in the data
        """
        return decrypted_data.count(1)
    
    def count_transitions(self, decrypted_data):
        """
        Count how many times the value (1 since the query values is 1 in the decryption) jumps to other values in the hypnogram's values.
        """
        transitions = 0
        for i in range(len(decrypted_data) - 1):
            if decrypted_data[i] == 1 and decrypted_data[i + 1] != 1:
                transitions += 1
        return transitions

    def count_sequences(self, decrypted_data):
        """
        Count how many distinct sequences of the value (1 since the query values is 1 in the decryption) appear in the hypnogram's values.
        """
        sequences = 0
        in_sequence = False
        for value in decrypted_data:
            if value == 1:
                if not in_sequence:  # Start of a new sequence
                    sequences += 1
                    in_sequence = True
            else:
                in_sequence = False  # End of the current sequence
        return sequences





