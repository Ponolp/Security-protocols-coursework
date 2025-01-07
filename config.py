# config.py
# Example values for SPADE configuration
MODULUS = 340282366920938463463374607431768211507  # Example prime modulus
GENERATOR = 2  # Example generator
MAX_PT_VEC_SIZE = 1000  # Max plaintext vector size, sets the mpk ans msk also to this size

# Database configurations
DbName = "database.sqlite"
TbName = "users_cipher"

# Number of users for the testing files (hypnogram.py, dna.py, test_app.py)
NumUsers = 10

# Padding configurations
PaddingItem = 20    # DNA goes to 16, hypnogram to 10, so 20 works

# Number of files to process (put a big value (>6000) if the whole dataset should be processed)
MaxFiles = 10000

# Define constants for the API endpoint
BASE_URL_ENCRYPT_HYPNO = "http://localhost:5000/hypnogram/register"
BASE_URL_QUERY_HYPNO = "http://localhost:5000/analyst/query_hypno"
BASE_URL_ENCRYPT_DNA = "http://localhost:5000/dna/register"
BASE_URL_QUERY_DNA = "http://localhost:5000/analyst/query_dna"

# Directories
HYPNO_DIR = './datasets/hypnogram'
DNA_DIR = './datasets/dna'