from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

class EncryptDecrypt:
    def __init__(self):
        self.__public_key = None
        self.__private_key = None

    @property
    def PublicKey(self):
        return self.__public_key
    
    @property
    def PrivateKey(self):
        return self.__private_key

    def GenerateKey(self):
        key = RSA.generate(2048)
        self.__private_key = key.export_key()
        self.__public_key = key.publickey().export_key()
    
    def ExportPublicKey(self, part="receiver.pem"):
        with open(part, mode="wb") as f:
            f.write(self.__public_key)
    
    def ExportPrivateKey(self, part="private.pem"):
        with open(part, mode="wb") as f:
            f.write(self.__private_key)


    def Encrypt(self, public_key, data):
        data = data.encode("utf-8")
        recipient_key = RSA.import_key(public_key)
        session_key = get_random_bytes(16)
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)

        return enc_session_key+cipher_aes.nonce+tag+ciphertext
    

    def Decrypt(self, data):
        private_key = RSA.import_key(self.__private_key)
        prvl = private_key.size_in_bytes()
        
        enc_session_key = data[0:prvl]
        nonce = data[prvl:prvl+16]
        tag = data[prvl+16:prvl+32]
        ciphertext = data[prvl+32:]

        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        return data.decode("utf-8")
