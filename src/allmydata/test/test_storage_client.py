
from twisted.trial import unittest
from twisted.internet import defer
from allmydata.storage_client import NativeStorageServer
from allmydata import storage_client
from allmydata.util import base32, pollmixin


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

class TestStorageFarmBroker(unittest.TestCase, pollmixin.PollMixin):
    def test_connected_thresh(self):

        upload_ready_d = defer.Deferred()
        sb = storage_client.StorageFarmBroker(None, True, 1, upload_ready_d)

        # announce 5 storage servers
        for k in ["%d" % i for i in range(5)]:
            ann = {"anonymous-storage-FURL": "pb://abcde@nowhere/fake",
                   "permutation-seed-base32": base32.b2a(k),
                   "service-name": "storage" }
            #sb.test_add_rref(k, "rref", ann)
            sb._got_announcement("v0-"+k, ann)

        # wait to connect
        def debug_wait_for_client_connections(num_clients):
            """Return a Deferred that fires (with None) when we have connections
            to the given number of peers. Useful for tests that set up a
            temporary test network and need to know when it is safe to proceed
            with an upload or download."""
            def _check():
                return len(sb.get_connected_servers()) >= num_clients
            d = self.poll(_check, 0.5)
            d.addCallback(lambda res: None)
            return d
        #debug_wait_for_client_connections(5)

        self.failUnlessEqual(len(sb.get_connected_servers()), 5)

        #return upload_ready_d


