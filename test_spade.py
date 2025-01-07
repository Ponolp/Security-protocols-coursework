import random
import spade
import time

def random_element_in_zmod(modulus):
    # Example implementation of random element in Zmod
    return random.randint(1, modulus - 1)

if __name__ == "__main__":
    
    n = 12
    q = 340282366920938463463374607431768211507
    g = 2
    sks = [random_element_in_zmod(q) for _ in range(n)]
    pks = [pow(g, sk, q) for sk in sks]
    alpha = random.randint(1, q - 1)

    data = [1, 2, 7, 7, 5, 9, 10, 7, 7, 7, 1, 1]
    value = 7
    
    reg_key = pow(g, alpha, q)

    spade_inmstance = spade.SPADE(q, g, n)

    dk = spade_inmstance.key_derivation(1, value, sks, reg_key)

    start_time = time.time()
    print(f"DATA: {data}")    
    
    c = spade_inmstance.encrypt(pks, alpha, data)
    print(f"ENCRYPT: {c}")

    d = spade_inmstance.decrypt(dk, value, c)
    print(f"DECRYPT: {d}")

    time_taken = time.time() - start_time
    print(f"Time taken: {time_taken:.10f}")