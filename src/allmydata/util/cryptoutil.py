
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
import scrypt
import base64
import binascii
import hashlib
import random

class AESCipher:
    block_size = 16
    padding = '-'

    def __init__(self):
        pass

    def generate_new_key(self, passphrase):
        not_stretched = hashlib.sha256(passphrase).digest()
        salt = not_stretched[:10] # XXX
        # XXX sufficiently paranoid?
        return scrypt.hash(not_stretched, salt, p=500, r=20, N=1024, buflen=32)

    def set_key(self, key):
        key_hash = SHA256.new(key).hexdigest()
        self.hmac_key = binascii.unhexlify(key_hash[len(key_hash)/2:])
        self.key = binascii.unhexlify(key_hash[:len(key_hash)/2])

    def verify_hmac(self, input_cipher, mac):
        local_hash = HMAC.new(self.hmac_key, digestmod=SHA256)
        local_hash.update(input_cipher)
        local_digest = local_hash.digest()
        return mac == local_digest

    def generate_hmac(self, input_cipher):
        local_hash = HMAC.new(self.hmac_key, digestmod=SHA256)
        local_hash.update(input_cipher)
        return local_hash.digest()

    def encrypt(self, plaintext):
        iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        cipher = AES.new(self.key, AES.MODE_CFB, iv, segment_size=128)

        pad = lambda s: s + (self.block_size - len(s) % self.block_size) * self.padding
        ciphertext = cipher.encrypt(pad(plaintext))
        mac = self.generate_hmac(ciphertext)

        return base64.b64encode(iv + ciphertext + mac)

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        hmac = enc[-32:]
        cipher_text = enc[16:-32]
        verified_hmac = self.verify_hmac((iv+cipher_text), hmac)
        if verified_hmac:
            cipher = AES.new(self.key, AES.MODE_CFB, iv, segment_size=128)
            return cipher.decrypt(cipher_text).rstrip(self.padding)
        else:
            return None
