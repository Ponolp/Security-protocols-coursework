import sqlite3
import json
from typing import List, Tuple, Optional

# Use Python's built-in `int` type for handling large integers.

class PBHandler:
    @staticmethod
    def read_public_params(response):
        """Unmarshal public parameters from the server response."""
        # Convert 'q' and 'g' from hex to int
        q = int(response['q'], 16)  # Base 16 to convert from hex string to integer
        g = int(response['g'], 16)  # Same for g

        # Convert each element in 'mpk' from hex to int
        mpk = [int(param, 16) for param in response['mpk']]  # Convert each hex string to int

        return q, g, mpk

    @staticmethod
    def read_decryption_key(response, err) -> Tuple[Optional[List[int]], Optional[List[List[int]]], Optional[Exception]]:
        if err:
            return None, None, err

        # Unmarshal dkv
        dkv = [int.from_bytes(dkv_bytes, byteorder='big') for dkv_bytes in response.dkv]

        # Unmarshal ciphertext
        cts = []
        for i in range(0, len(response.ciphertext), 2):
            c0 = int.from_bytes(response.ciphertext[i], byteorder='big')
            c1 = int.from_bytes(response.ciphertext[i + 1], byteorder='big')
            cts.append([c0, c1])

        return dkv, cts, None


class DBHandler:
    def __init__(self, db_name: str, table_name: str):
        self.db_name = db_name
        self.table_name = table_name
        self.conn = self._create_connection()

    def _create_connection(self):
        try:
            conn = sqlite3.connect(self.db_name)
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None

    def create_users_cipher_table(self) -> None:
        """Create the users cipher table if it does not exist."""
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INTEGER PRIMARY KEY,
            reg_key BLOB NOT NULL,
            ciphertext BLOB NOT NULL
        );
        """
        try:
            with self.conn:
                self.conn.execute(query)
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
            raise

    def insert_users_cipher(self, data) -> None:
        """Insert user request data into the database."""
        ctx = self._serialize_ciphertext(data['ciphertext'])
        query = f"INSERT INTO {self.table_name} (id, reg_key, ciphertext) VALUES (?, ?, ?)"
        try:
            with self.conn:
                self.conn.execute(query, (data['id'], data['regKey'], ctx))
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")
            raise

    def get_user_req_by_id(self, user_id: int):
        """Retrieve user request data from the database by ID."""
        query = f"SELECT reg_key, ciphertext FROM {self.table_name} WHERE id = ?"
        try:
            with self.conn:
                cursor = self.conn.execute(query, (user_id,))
                row = cursor.fetchone()
                if not row:
                    return None

                reg_key = row[0]
                ciphertext = self._deserialize_ciphertext(row[1])
                return {"id": user_id, "reg_key": reg_key, "ciphertext": ciphertext}
        except sqlite3.Error as e:
            print(f"Error retrieving data: {e}")
            raise

    def _serialize_ciphertext(self, ciphertext: List[List[bytes]]) -> bytes:
        """Serialize the ciphertext for storage."""
        # Flatten the ciphertext list and convert each byte element to hex
        flattened_hex = []
        for ct_pair in ciphertext:  # Each ct_pair is a list like [c0, c1]
            for ct in ct_pair:  # ct is a byte object (either c0 or c1)
                flattened_hex.append(ct.hex())  # Convert each byte object to a hex string
    
        # Convert the flattened list of hex strings to a JSON-encoded byte string
        return json.dumps(flattened_hex).encode()

    def _deserialize_ciphertext(self, serialized: bytes) -> List[List[bytes]]:
        """Deserialize the stored ciphertext into pairs of [c0, c1]."""
        # Decode the JSON-encoded serialized data into a list of hex strings
        flattened_hex = json.loads(serialized.decode())
    
        # Rebuild the ciphertext list as pairs of [c0, c1] bytes
        ciphertext = []
        for i in range(0, len(flattened_hex), 2):  # Step by 2, because each ciphertext entry is a pair
            c0 = bytes.fromhex(flattened_hex[i])  # Convert the first element in the pair to bytes
            c1 = bytes.fromhex(flattened_hex[i + 1])  # Convert the second element in the pair to bytes
            ciphertext.append([c0, c1])  # Append the pair as a list [c0, c1]
    
        return ciphertext


    def close_connection(self) -> None:
        if self.conn:
            self.conn.close()
