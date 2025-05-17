from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os.path
import hashlib
import random, sys, os
import shutil

# AES
class Encryptor:
    def __init__(self, key):
        self.key = key

    def pad(self, s):
        return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

    def encrypt(self, message, key, key_size=256):
        message = self.pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(message)

    def encrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            plaintext = fo.read()
        enc = self.encrypt(plaintext, self.key)
        with open(file_name + ".enc", 'wb') as fo:
            fo.write(enc)
        os.remove(file_name)

    def decrypt(self, ciphertext, key):
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")

    def decrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            ciphertext = fo.read()
        dec = self.decrypt(ciphertext, self.key)
        with open(file_name[:-4], 'wb') as fo:
            fo.write(dec)
        os.remove(file_name)
# AES - end

# RSA
def power(a, n, p):
    res = 1
    a = a % p 

    while n > 0:         
        if n % 2:
            res = (res * a) % p
            n = n - 1
        else:
            a = (a ** 2) % p
            n = n // 2
             
    return res % p

def gcd(a, b):
   while a != 0:
      a, b = b % a, a
   return b

def findModInverse(a, m):
   if gcd(a, m) != 1:
      return None
   u1, u2, u3 = 1, 0, a
   v1, v2, v3 = 0, 1, m
   
   while v3 != 0:
    q = u3 // v3
    v1, v2, v3, u1, u2, u3 = (u1 - q * v1), (u2 - q * v2), (u3 - q * v3), v1, v2, v3
   return u1 % m
     
def isPrime(n, k):
    if n == 1 or n == 4:
        return False
    elif n == 2 or n == 3:
        return True
    else:
        for i in range(k):             
            # Chọn 1 số ngẫu nhiên trong [2..n-2] Để đảm bảo rằng n luôn lớn hơn 4
            a = random.randint(2, n - 2)
             
            # Fermat nhỏ
            if power(a, n - 1, n) != 1:
                return False                 
    return True

def generateLargePrime(keysize):
   while True:
      num = random.randrange(2**(keysize-1), 2**(keysize))
      if isPrime(num, 3):
         return num

def generateKey(keySize):
   p = generateLargePrime(keySize)
   q = generateLargePrime(keySize)
   n = p * q
	
   while True:
      e = random.randrange(2 ** (keySize - 1), 2 ** (keySize))
      if gcd(e, (p - 1) * (q - 1)) == 1:
         break

   d = findModInverse(e, (p - 1) * (q - 1))
   publicKey = (n, e)
   privateKey = (n, d)
   return (publicKey, privateKey)

def Encrypt(msg,e,n):
    luuchuoi = []
    for i in msg:
        c = power(ord(i),e,n)
        luuchuoi.append(str(c))
    return luuchuoi

def Decrypt(luuchuoi, d, n):
    msg2 = ""
    for i in luuchuoi:
        de = power(int(i),d,n)
        msg2+=chr(de)
    return msg2

def makeKeyFilesAlice (name, keySize):
        publicKey, privateKey = generateKey(keySize)
        with open(name, 'w', encoding='utf-8') as f:
            f.write(f'PublicKey: ({publicKey[0]},{publicKey[1]})\n')
            f.write(f'PrivateKey: ({privateKey[0]},{privateKey[1]})\n')
            #f.write(''.join(f'{publicKey[0]} {publicKey[1]}'))
        return (publicKey, privateKey)

def makeKeyFilesBob(name, name1, keySize):
        publicKey, privateKey = generateKey(keySize)

        with open(name, 'w', encoding='utf-8') as f:
            f.write(''.join(f'{publicKey[0]} {publicKey[1]}'))
        with open(name1, 'w', encoding='utf-8') as f:
            f.write(''.join(f'{privateKey[0]} {privateKey[1]}'))
# RSA - end

# SHA
def HashToId(file):
    BLOCK_SIZE = 65536 # Kích thước của khối

    file_hash = hashlib.sha256() # Tạo đối tượng Hash
    with open(file, 'rb') as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            file_hash.update(fb) # Cập nhật fb vào file_hash
            fb = f.read(BLOCK_SIZE) # Đọc những dòng còn lại của file
            id = file_hash.hexdigest() # Hàm trả về 1 chuỗi hex đại diện cho hàm băm
    return id
# SHA - end

# Read & Write Files
def WriteToFiles(name, id):
    with open(name, 'w', encoding='utf-8') as f:
                f.write(" ".join(id))

def ReadKey(name, charactertemp):
    with open(name, 'r') as file:
        contents = file.read()

        character = charactertemp

        result = contents.split(character)
    return result
# Read & Write Files - end