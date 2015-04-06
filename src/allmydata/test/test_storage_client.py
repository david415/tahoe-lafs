
from twisted.trial import unittest
from twisted.internet import defer
from allmydata.storage_client import NativeStorageServer


class NativeStorageServerWithVersion(NativeStorageServer):
    def __init__(self,version):
        self.version=version
    def get_version(self):
        return self.version


class TestNativeStorageServer(unittest.TestCase):
    def test_get_available_space_new(self):
        nss = NativeStorageServerWithVersion(
            { "http://allmydata.org/tahoe/protocols/storage/v1":
                { "maximum-immutable-share-size": 111,
                  "available-space": 222,
                }
            })
        self.failUnlessEqual(nss.get_available_space(), 222)

    def test_get_available_space_old(self):
        nss = NativeStorageServerWithVersion(
            { "http://allmydata.org/tahoe/protocols/storage/v1":
                { "maximum-immutable-share-size": 111,
                }
            })
        self.failUnlessEqual(nss.get_available_space(), 111)

class TestStorageFarmBroker(unittest.TestCase):
    def test_connected_thresh(self):

        connected_deferred = defer.Deferred()
        sb = StorageFarmBroker(None, True, 1, connected_deferred)
        for k in ["%d" % i for i in range(5)]:
            ann = {"anonymous-storage-FURL": "pb://abcde@nowhere/fake",
                   "permutation-seed-base32": base32.b2a(k) }
        sb.test_add_rref(k, "rref", ann)
        self.failUnlessEqual(broker.get_connected_servers(), 5)
