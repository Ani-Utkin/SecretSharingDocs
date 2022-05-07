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
    r_text = ""
    for j in shares:
        
        r = (int)(SSS.reconstruct_secret(j))
        r_text += chr(r)

    return r_text
