# Coursework for security protocols course
This is the program for the coursework 2 in the course COMP.SEC.220-Coursework2 by Lauri Pollari.
It implements the SPADE scheme and allows partial decryption from the database with a value. Value must be in the dataset.

## README
The SPADE algorhitm I have tested to be working correctly. Use of the data and users isn't perfected.
Some files/functions may have not have been used, in utils for example. Performance time with greater datasets isn't great.

## How to run the program
1. CHECK THE CONFIG: the value of MAX_PT_VEC_SIZE sets the size of the keys and plaintext and ciphertext. 
   There is padding if the data isn't long enough (only when files are processed via utils).

2. Add the datasets to the datasets folder (should be datasets/dna and datasets/hypnogram).
   Currently only has 3 hypnogram files in git.

4. Run the server on command window (I have used bash): Python app.py
   NOTE!: If the server restarts and the database isn't removed, the decryption won't work on the old data since the keys are changed.

5. There are test files for both usecases: dna.py and hypnogram.py
   NOTE!: Set the desired user amount and vector size in the config file.
    To run these: Python TESTFILENAME
    The tests are slow though (about 2s per user), when making POST requests straight from the server, the time is much faster.
    I don't recommend running with too many users, like over 100.

   There are also testfiles for analyst usecases and the spade itself: analyst_usecases.py and test_spade.py
   NOTE!: There is no padding so MAX_PT_VEC_SIZE should be set to same as the data vector size
    To run these: Python TESTFILENAME   (Check the configs and query id and value (must be in database)!!)

6. If one wants to make queries themself, it is possible to make requests, examples below 
   NOTE!: There is no padding so MAX_PT_VEC_SIZE should be set to same as the data vector size (e.g. 12 for the ones below)

    curl -X POST http://localhost:5000/dna/register \
     -H "Content-Type: application/json" \
     -d '{"user_id": 13, "data": [1, 2, 3, 4, 3, 3, 8, 3, 3, 3, 15, 16]}'

    curl -X POST http://localhost:5000/analyst/query_dna \
     -H "Content-Type: application/json" \
     -d '{"user_id": 13, "query_value": "AG"}'

    curl -X POST http://localhost:5000/hypnogram/register \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "data":[1, 2, 7, 7, 5, 9, 10, 7, 7, 7, 1, 1]}'

    curl -X POST http://localhost:5000/analyst/query_hypno \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "query_value": 7}'

7. There is a file to try the benchmark without the use of server: test_app.py
   It's more suitable for more users, though the prints may take a while.
   To run this: python test_app.py   (server should not be running!!)

  The query response gives the decrypted data where values 1 are the query values.

Database.sqlite is initialized and removed when the app.py is run and closed. Close the app with ctrl+c.
To see database: sqlite3 database.sqlite
                 SELECT * FROM users_cipher

SCREENCAST OF THE PROGRAM RUNNING: https://drive.google.com/file/d/1U7vBRdpC5Prw0jmvUK4-rK2f-cpAom8w/view?usp=sharing
