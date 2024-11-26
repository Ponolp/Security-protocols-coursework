import argparse
from src import algorithms, key_curator, user_operations, data_analyst

def setup_spade(args):
    """Handles setup phase."""
    msk, mpk = algorithms.setup(args.n, args.q, args.g)
    print("Setup Complete")
    print("Master Secret Key (msk):", msk)
    print("Master Public Key (mpk):", mpk)

def encrypt_data(args):
    """
    Encrypt the data in the specified directory using SPADE.
    """
    # Load all .txt files from the dataset directory
    dataset_files = load_files_from_directory(args.data_dir)
    print(f"Loaded {len(dataset_files)} files from {args.data_dir}")
    
    # Encrypt each file’s data
    for file_content in dataset_files:
        # Parse the file data into integers (DNA sequences)
        x = parse_data(file_content)
        
        # Perform encryption
        h, c = user_operations.enc(args.mpk, x, args.alpha, args.g, args.q)  # Perform encryption
        
        # Optionally, print or store the encrypted data
        print(f"Encrypted data: {c}")


def decrypt_data(args):
    """Handles decryption of data."""
    dk = key_curator.key_der(args.msk, args.value, args.alpha, args.g, args.q)
    y = data_analyst.dec(dk, args.ciphertext, args.helping_info, args.value, args.g, args.q)
    print("Decryption Result (y):", y)

def evaluate(args):
    """
    Run evaluation on the specified dataset directory based on the task.
    """
    # Load all .txt files from the dataset directory
    dataset_files = load_files_from_directory(args.dataset_dir)
    print(f"Loaded {len(dataset_files)} files from {args.dataset_dir}")
    
    # Process each file based on the task type (hypnogram/genomic)
    for file_content in dataset_files:
        # Example: Parse data from the file content
        x = parse_data(file_content)
        
        # Perform task-specific evaluation
        if args.task == "hypnogram":
            result = evaluate_hypnogram(x)  # Define this function for task-specific logic
        elif args.task == "genomic":
            result = evaluate_genomic(x)  # Define this function for task-specific logic
        
        print(f"Evaluation result for file: {result}")

def evaluate_hypnogram(x):
    """
    Hypnogram-specific evaluation logic.
    """
    # Your logic for evaluating the hypnogram data goes here
    return f"Hypnogram evaluation for {x}"

def evaluate_genomic(x):
    """
    Genomic-specific evaluation logic.
    """
    # Your logic for evaluating genomic data goes here
    return f"Genomic evaluation for {x}"

import os
import glob

def load_files_from_directory(directory_path):
    """
    Loads all text files from a specified directory.

    Args:
        directory_path (str): Path to the dataset directory.

    Returns:
        list of str: A list of file contents.
    """
    # Get a list of all .txt files in the directory
    txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
    
    # Read the contents of each file
    files_content = []
    for file_path in txt_files:
        with open(file_path, 'r') as file:
            files_content.append(file.read())  # Add the file content to the list
    
    return files_content

# Example usage:
# dna_files = load_files_from_directory("datasets/dna")
# hypnogram_files = load_files_from_directory("datasets/hypnogram")

def parse_data(file_content):
    """
    Parse the content of a file into a format that can be used for evaluation.
    For DNA sequences, we convert the bases A, C, G, T into integers.

    Args:
        file_content (str): The content of a dataset file (e.g., a DNA sequence).

    Returns:
        list: Parsed data as a list of integers representing the DNA sequence.
    """
    # Define a mapping for DNA bases to integers
    dna_to_int = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    
    # Initialize a list to hold the converted sequence
    parsed_data = []

    # Convert each line (DNA sequence) into a list of integers
    for line in file_content.splitlines():
        sequence = [dna_to_int[base] for base in line.strip() if base in dna_to_int]
        parsed_data.extend(sequence)

    return parsed_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SPADE Cryptographic Scheme Implementation")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Setup Command
    setup_parser = subparsers.add_parser("setup", help="Run setup for SPADE")
    setup_parser.add_argument("--n", type=int, required=True, help="Number of entries")
    setup_parser.add_argument("--q", type=int, required=True, help="Fermat prime modulus")
    setup_parser.add_argument("--g", type=int, required=True, help="Base of cyclic group")
    setup_parser.set_defaults(func=setup_spade)
    
    # Encryption Command
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt data")
    encrypt_parser.add_argument("--mpk", nargs="+", required=True, type=int, help="Master Public Key")
    encrypt_parser.add_argument("--alpha", type=int, required=True, help="User's secret key")
    encrypt_parser.add_argument("--g", type=int, required=True, help="Base of cyclic group")
    encrypt_parser.add_argument("--q", type=int, required=True, help="Fermat prime modulus")
    encrypt_parser.add_argument("--data_dir", type=str, required=True, help="Path to dataset directory")
    encrypt_parser.set_defaults(func=encrypt_data)

    
    # Decryption Command
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt data")
    decrypt_parser.add_argument("--msk", nargs="+", required=True, type=int, help="Master Secret Key")
    decrypt_parser.add_argument("--ciphertext", nargs="+", required=True, type=int, help="Ciphertext")
    decrypt_parser.add_argument("--helping_info", nargs="+", required=True, type=int, help="Helping Information (h)")
    decrypt_parser.add_argument("--alpha", type=int, required=True, help="User's secret key")
    decrypt_parser.add_argument("--value", type=int, required=True, help="Value to check in message")
    decrypt_parser.add_argument("--g", type=int, required=True, help="Base of cyclic group")
    decrypt_parser.add_argument("--q", type=int, required=True, help="Fermat prime modulus")
    decrypt_parser.add_argument("--data_dir", type=str, required=True, help="Path to dataset directory")
    decrypt_parser.set_defaults(func=decrypt_data)

    
    # Evaluate Command
    evaluate_parser = subparsers.add_parser("evaluate", help="Run evaluation on datasets")
    evaluate_parser.add_argument("--dataset_dir", type=str, required=True, help="Path to dataset directory")
    evaluate_parser.add_argument("--task", type=str, choices=["hypnogram", "genomic"], required=True, help="Dataset type")
    evaluate_parser.set_defaults(func=evaluate)
    
    # Parse Arguments
    args = parser.parse_args()
    args.func(args)
