import SSS
import random

def SSSText(text):
    
    shares = []

    for i in text:
        i = ord(i)
        share = SSS.generate_shares(3, 2, i)
        shares.append(share)
    
    return shares

def SSS_reconstruct(shares):
    
    for j in shares:

        pool = random.sample(j, 2)

        r = SSS.reconstruct_secret(pool)
        r_text += chr(r)

    return r_text