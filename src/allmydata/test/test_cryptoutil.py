
from twisted.trial import unittest

from allmydata.util.cryptoutil import AESCipher

class TestAESCipher(unittest.SynchronousTestCase):
    def test_all(self):
        print "test all"
        c = AESCipher()
        passphrase = "a mouse in a house by the river"
        print "generate key"
        key = c.generate_new_key(passphrase)
        c.set_key(key)
        plaintext = "castles built upon slippery slopes of slate"
        print "encrypt plaintext"
        ciphertext = c.encrypt(plaintext)
        print "ciphertext %r" % (ciphertext,)
        print "decrypt ciphertext"
        plaintext2 = c.decrypt(ciphertext)
        print "plaintext2 %r" % (plaintext2,)

