from Crypto.Cipher import AES
import base64

BLOCK_SIZE = 16
key = b"c35c0607957d96fd"

def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + chr(length)*length

def unpad(data):
    return data[:-ord(chr(data[-1]))]

def decrypt(encrypted):
    encrypted = base64.b64decode(encrypted)
    IV = encrypted[:BLOCK_SIZE]
    aes = AES.new(key, AES.MODE_CBC, IV)
    decrypted = aes.decrypt(encrypted[BLOCK_SIZE: ])
    return unpad(decrypted)