import os
import random
import json
from pathlib import Path
from math import log2, gcd  # Added gcd import from math
from typing import List, Tuple
from math import ceil
import struct
import config

PORT = 50505


def handle_error(e: Exception):
    """Handle errors by raising them."""
    if e:
        raise e

def process_hypnogram_files(directory):
    """
    Process all hypnogram files in the specified directory.
    Each file is expected to contain a sequence of integer values (sleep stages).
    """
    hypnogram_data = []
    counter = 0
    # Iterate over all text files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            with open(file_path, 'r') as file:
                # Read the file and convert it to a list of integers
                file_data = file.read().strip().split()
                file_data = [int(x) for x in file_data]
                padded_data = add_padding(config.PaddingItem, config.MAX_PT_VEC_SIZE, file_data)
                hypnogram_data.append(padded_data)  # Append to the main list
                counter += 1
                if counter == config.MaxFiles:
                    break 
            
    return hypnogram_data

def process_dna_files(directory):
    """
    Open DNA files from the dataset directory.
    Assumption: one file per user.
    """
    
    try:
        files = os.listdir(directory)
    except Exception as e:
        print(f"Error reading dataset directory: {e}")
        return []
    
    print(f"Reading {len(files)} files...")
    
    dna_data = []
    counter = 0
    # Iterate over all text files in the directory
    for filename in files:
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            dna_seq = read_dna_seq_file(file_path)
            dinucs = convert_dna_seq_to_dinucleotide(dna_seq)
            mapped_dinucs = map_dinucleotide_to_int(dinucs)
            padded_data = add_padding(config.PaddingItem, config.MAX_PT_VEC_SIZE, mapped_dinucs)
            dna_data.append(padded_data)
            counter += 1
            if counter == config.MaxFiles:
                break 
        
    return dna_data # Remove the outer list

# Normalize hypnogram datasets
def normalize_hypnogram_datasets(dir_path: str, norm_val: int):
    files = list(Path(dir_path).glob("*.txt"))
    print(f"Number of files: {len(files)}")

    for file in files:
        with open(file, "r") as f:
            integers = [int(line.strip()) + norm_val for line in f]

        with open(file, "w") as f:
            f.writelines(f"{i}\n" for i in integers)

        print(f"Successfully modified and saved file: {file}")


# Read hypnogram file
def read_hypnogram_file(path: str) -> List[int]:
    try:
        with open(path, "r") as file:
            return [int(line.strip()) for line in file]
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return []


# Save data to a file
def save_in_file(path: str, data: List[List[int]]):
    try:
        with open(path, "w") as file:
            for row in data:
                file.write(" ".join(str(num) for num in row) + "\n")
    except Exception as e:
        print(f"Error saving file {path}: {e}")


# Delete file
def delete_file(path: str):
    try:
        os.remove(path)
        print(f"Successfully deleted file: {path}")
    except Exception as e:
        print(f"Error deleting file {path}: {e}")


# Add padding to an array
def add_padding(padding_item: int, max_length: int, data: List[int]) -> List[int]:
    return data[:max_length] + [padding_item] * max(0, max_length - len(data))


# Generate dummy data
def gen_dummy_data(num_users: int, pt_vec_size: int, max_value: int) -> List[List[int]]:
    return [[random.randint(1, max_value) for _ in range(pt_vec_size)] for _ in range(num_users)]


# Print a big integer in hexadecimal format
def print_big_int_hex(label: str, n: int):
    print(f">>> {label}: {hex(n)}")


# Verify decryption results
def verify_results(original_data: List[int], res: List[int], v: int):
    n_match_els = sum(1 for i, val in enumerate(original_data) if val == v and res[i] != 1)
    if n_match_els:
        print(f"=== FAIL: There are {n_match_els} mismatched elements!")
    else:
        print("=== PASS: Hooray!")


# Read DNA sequence file
def read_dna_seq_file(filename: str) -> List[str]:
    try:
        with open(filename, "r") as file:
            return [line.strip() for line in file]
    except Exception as e:
        print(f"Error reading DNA sequence file {filename}: {e}")
        return []


# Convert DNA sequence to dinucleotide (2-base pairs)
def convert_dna_seq_to_dinucleotide(dna_seq: List[str]) -> List[str]:
    dinucleotides = []
    for sequence in dna_seq:
        # Loop through the sequence, taking each pair of bases
        for i in range(len(sequence) - 1):
            dinucleotides.append(sequence[i:i + 2])
    return dinucleotides


# Map dinucleotide to integers
def map_dinucleotide_to_int(dinucleotides: List[str]) -> List[int]:
    dinu_map = {
        "AA": 1, "AC": 2, "AG": 3, "AT": 4,
        "CA": 5, "CC": 6, "CG": 7, "CT": 8,
        "GA": 9, "GC": 10, "GG": 11, "GT": 12,
        "TA": 13, "TC": 14, "TG": 15, "TT": 16
    }
    return [dinu_map.get(dinu, 0) for dinu in dinucleotides]

def random_element_in_zmod(modulus):
    # Example implementation of random element in Zmod
    return random.randint(1, modulus - 1)
