def dec(dk, c, h, v, g, q):
    y = []
    for ci, hi, ki in zip(c, h, dk):
        temp = (ci * pow(hi, -v, q) * ki) % q
        y.append(temp)
    return y

# Example usage
# y = dec(dk, c, h, v, g, q)
# print("Decrypted Results (y):", y)

# Interpretation: y[i] = 1 iff x[i] = v
# result = [1 if yi == 1 else 0 for yi in y]
# print("Result Vector:", result)
