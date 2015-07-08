
import os, sys, stat, time

from twisted.trial import unittest
from twisted.internet import defer

from allmydata.interfaces import IDirectoryNode

from allmydata.util import fake_inotify, fileutil
from allmydata.util.encodingutil import get_filesystem_encoding, to_filepath
from allmydata.util.consumer import download_to_data
from allmydata.test.no_network import GridTestMixin
from allmydata.test.common_util import ReallyEqualMixin, NonASCIIPathMixin
from allmydata.test.common import ShouldFailMixin
from allmydata.test.test_cli_magic_folder import MagicFolderCLITestMixin

from allmydata.frontends import magic_folder
from allmydata.frontends.magic_folder import MagicFolder
from allmydata import backupdb
from allmydata.util.fileutil import abspath_expanduser_unicode

class MagicFolderTestMixin(MagicFolderCLITestMixin, ShouldFailMixin, ReallyEqualMixin, NonASCIIPathMixin):
    """
    These tests will be run both with a mock notifier, and (on platforms that support it)
    with the real INotify.
    """

    def setUp(self):
        GridTestMixin.setUp(self)
        temp = self.mktemp()
        self.basedir = abspath_expanduser_unicode(temp.decode(get_filesystem_encoding()))
        self.magicfolder = None
        self.dir_node = None

    def _get_count(self, name):
        return self.stats_provider.get_stats()["counters"].get(name, 0)

    def _createdb(self):
        dbfile = abspath_expanduser_unicode(u"magicfolderdb.sqlite", base=self.basedir)
        bdb = backupdb.get_backupdb(dbfile, create_version=(backupdb.SCHEMA_v3, 3))
        self.failUnless(bdb, "unable to create backupdb from %r" % (dbfile,))
        self.failUnlessEqual(bdb.VERSION, 3)
        return bdb

    def _made_upload_dir(self, n):
        if self.dir_node == None:
            self.dir_node = n
        else:
            n = self.dir_node
        self.failUnless(IDirectoryNode.providedBy(n))
        self.upload_dirnode = n
        self.upload_dircap = n.get_uri()
        self.collective_dircap = ""

    def _create_magicfolder(self, ign):
        dbfile = abspath_expanduser_unicode(u"magicfolderdb.sqlite", base=self.basedir)
        self.magicfolder = MagicFolder(self.client, self.upload_dircap, self.collective_dircap, self.local_dir,
                                       dbfile, inotify=self.inotify, pending_delay=0.2)
        self.magicfolder.setServiceParent(self.client)
        self.magicfolder.ready()

    # Prevent unclean reactor errors.

    def test_db_basic(self):
        fileutil.make_dirs(self.basedir)
        self._createdb()

    def test_db_persistence(self):
        """Test that a file upload creates an entry in the database."""

        fileutil.make_dirs(self.basedir)
        db = self._createdb()

        path = abspath_expanduser_unicode(u"myFile1", base=self.basedir)
        db.did_upload_file('URI:LIT:1', path, 1, 0, 0, 33)

        c = db.cursor
        c.execute("SELECT size,mtime,ctime,fileid"
                  " FROM local_files"
                  " WHERE path=?",
                  (path,))
        row = db.cursor.fetchone()
        self.failIfEqual(row, None)

        # Second test uses db.check_file instead of SQL query directly
        # to confirm the previous upload entry in the db.
        path = abspath_expanduser_unicode(u"myFile2", base=self.basedir)
        fileutil.write(path, "meow\n")
        s = os.stat(path)
        size = s[stat.ST_SIZE]
        ctime = s[stat.ST_CTIME]
        mtime = s[stat.ST_MTIME]
        db.did_upload_file('URI:LIT:2', path, 1, mtime, ctime, size)
        r = db.check_file(path)
        self.failUnless(r.was_uploaded())

    def test_magicfolder_start_service(self):
        self.set_up_grid()

        self.local_dir = abspath_expanduser_unicode(self.unicode_or_fallback(u"l\u00F8cal_dir", u"local_dir"),
                                                    base=self.basedir)
        self.mkdir_nonascii(self.local_dir)

        self.client = self.g.clients[0]
        self.stats_provider = self.client.stats_provider

        d = self.client.create_dirnode()
        d.addCallback(self._made_upload_dir)
        d.addCallback(self._create_magicfolder)
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.dirs_monitored'), 1))
        d.addBoth(self.cleanup)
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.dirs_monitored'), 0))
        return d

    def test_move_tree(self):
        self.set_up_grid()

        self.local_dir = abspath_expanduser_unicode(self.unicode_or_fallback(u"l\u00F8cal_dir", u"local_dir"),
                                                    base=self.basedir)
        self.mkdir_nonascii(self.local_dir)

        self.client = self.g.clients[0]
        self.stats_provider = self.client.stats_provider

        empty_tree_name = self.unicode_or_fallback(u"empty_tr\u00EAe", u"empty_tree")
        empty_tree_dir = abspath_expanduser_unicode(empty_tree_name, base=self.basedir)
        new_empty_tree_dir = abspath_expanduser_unicode(empty_tree_name, base=self.local_dir)

        small_tree_name = self.unicode_or_fallback(u"small_tr\u00EAe", u"empty_tree")
        small_tree_dir = abspath_expanduser_unicode(small_tree_name, base=self.basedir)
        new_small_tree_dir = abspath_expanduser_unicode(small_tree_name, base=self.local_dir)

        d = self.create_invite_join_magic_folder(u"Alice", self.local_dir)
        d.addCallback(self._create_magicfolder)

        def _check_move_empty_tree(res):
            self.mkdir_nonascii(empty_tree_dir)
            d2 = defer.Deferred()
            self.magicfolder.set_processed_callback(d2.callback, ignore_count=0)
            os.rename(empty_tree_dir, new_empty_tree_dir)
            self.notify(to_filepath(new_empty_tree_dir), self.inotify.IN_MOVED_TO)
            return d2
        d.addCallback(_check_move_empty_tree)
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_succeeded'), 1))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.files_uploaded'), 0))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_queued'), 0))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.directories_created'), 1))

        def _check_move_small_tree(res):
            self.mkdir_nonascii(small_tree_dir)
            fileutil.write(abspath_expanduser_unicode(u"what", base=small_tree_dir), "say when")
            d2 = defer.Deferred()
            self.magicfolder.set_processed_callback(d2.callback, ignore_count=1)
            os.rename(small_tree_dir, new_small_tree_dir)
            self.notify(to_filepath(new_small_tree_dir), self.inotify.IN_MOVED_TO)
            return d2
        d.addCallback(_check_move_small_tree)
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_succeeded'), 3))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.files_uploaded'), 1))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_queued'), 0))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.directories_created'), 2))

        def _check_moved_tree_is_watched(res):
            d2 = defer.Deferred()
            self.magicfolder.set_processed_callback(d2.callback, ignore_count=0)
            fileutil.write(abspath_expanduser_unicode(u"another", base=new_small_tree_dir), "file")
            self.notify(to_filepath(abspath_expanduser_unicode(u"another", base=new_small_tree_dir)), self.inotify.IN_CLOSE_WRITE)
            return d2
        d.addCallback(_check_moved_tree_is_watched)
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_succeeded'), 4))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.files_uploaded'), 2))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_queued'), 0))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.directories_created'), 2))

        # Files that are moved out of the upload directory should no longer be watched.
        def _move_dir_away(ign):
            os.rename(new_empty_tree_dir, empty_tree_dir)
            # Wuh? Why don't we get this event for the real test?
            #self.notify(to_filepath(new_empty_tree_dir), self.inotify.IN_MOVED_FROM)
        d.addCallback(_move_dir_away)
        def create_file(val):
            test_file = abspath_expanduser_unicode(u"what", base=empty_tree_dir)
            fileutil.write(test_file, "meow")
            return
        d.addCallback(create_file)
        d.addCallback(lambda ign: time.sleep(1))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_succeeded'), 4))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.files_uploaded'), 2))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_queued'), 0))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.directories_created'), 2))

        d.addBoth(self.cleanup)
        return d

    def test_persistence(self):
        """
        Perform an upload of a given file and then stop the client.
        Start a new client and magic-folder service... and verify that the file is NOT uploaded
        a second time. This test is meant to test the database persistence along with
        the startup and shutdown code paths of the magic-folder service.
        """
        print "calling set up grid"
        self.set_up_grid()
        self.local_dir = abspath_expanduser_unicode(u"test_persistence", base=self.basedir)
        self.mkdir_nonascii(self.local_dir)

        self.client = self.g.clients[0]
        self.stats_provider = self.client.stats_provider
        self.collective_dircap = ""

        d = self.create_invite_join_magic_folder(u"Alice", self.local_dir)
        d.addCallback(self._create_magicfolder)
        def create_test_file(result):
            d2 = defer.Deferred()
            self.magicfolder.set_processed_callback(d2.callback, ignore_count=0)
            test_file = abspath_expanduser_unicode(u"what", base=self.local_dir)
            fileutil.write(test_file, "meow")
            self.notify(to_filepath(test_file), self.inotify.IN_CLOSE_WRITE)
            return d2
        d.addCallback(create_test_file)
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_succeeded'), 1))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_queued'), 0))

        def restart(ignore):
            print "restart"
            tahoe_config_file = os.path.join(self.get_clientdir(), "tahoe.cfg")
            tahoe_config = fileutil.read(tahoe_config_file)
            d3 = defer.succeed(None)
            def write_config(client_node_dir):
                print "write_config"
                fileutil.write(os.path.join(client_node_dir, "tahoe.cfg"), tahoe_config)
            def setup_stats(result):
                print "setup_stats"
                self.client = None
                print "calling set up grid"
                self.set_up_grid(client_config_hooks={0: write_config})
                self.client = self.g.clients[0]
                self.stats_provider = self.client.stats_provider
                self.magicfolder = self.client.getServiceNamed("magic-folder")
                print "upload path ", self.magicfolder._local_dir
                print "ready ", self.magicfolder.is_ready
                d4 = defer.Deferred()
                self.magicfolder.set_processed_callback(d4.callback, ignore_count=0)
                return d4

            d3.addBoth(self.cleanup)
            d3.addCallback(setup_stats)
            return d3
        d.addCallback(restart)
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_succeeded'), 0))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_queued'), 0))
        d.addBoth(self.cleanup)
        return d

    def test_magic_folder(self):
        self.set_up_grid()
        self.local_dir = os.path.join(self.basedir, self.unicode_or_fallback(u"loc\u0101l_dir", u"local_dir"))
        self.mkdir_nonascii(self.local_dir)

        self.client = self.g.clients[0]
        self.stats_provider = self.client.stats_provider

        d = self.client.create_dirnode()

        d.addCallback(self._made_upload_dir)
        self.collective_dircap = ""
        d.addCallback(self._create_magicfolder)

        # Write something short enough for a LIT file.
        d.addCallback(lambda ign: self._check_file(u"short", "test"))

        # Write to the same file again with different data.
        d.addCallback(lambda ign: self._check_file(u"short", "different"))

        # Test that temporary files are not uploaded.
        d.addCallback(lambda ign: self._check_file(u"tempfile", "test", temporary=True))

        # Test that we tolerate creation of a subdirectory.
        d.addCallback(lambda ign: os.mkdir(os.path.join(self.local_dir, u"directory")))

        # Write something longer, and also try to test a Unicode name if the fs can represent it.
        name_u = self.unicode_or_fallback(u"l\u00F8ng", u"long")
        d.addCallback(lambda ign: self._check_file(name_u, "test"*100))

        # TODO: test that causes an upload failure.
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.files_failed'), 0))

        d.addBoth(self.cleanup)
        return d

    def _check_file(self, name_u, data, temporary=False):
        previously_uploaded = self._get_count('magic_folder.objects_succeeded')
        previously_disappeared = self._get_count('magic_folder.objects_disappeared')


        # Note: this relies on the fact that we only get one IN_CLOSE_WRITE notification per file
        # (otherwise we would get a defer.AlreadyCalledError). Should we be relying on that?
        self.magicfolder.set_processed_callback(d.callback)

        path_u = abspath_expanduser_unicode(name_u, base=self.local_dir)
        path = to_filepath(path_u)

        # We don't use FilePath.setContent() here because it creates a temporary file that
        # is renamed into place, which causes events that the test is not expecting.
        f = open(path_u, "wb")
        try:
            if temporary and sys.platform != "win32":
                os.unlink(path_u)
            f.write(data)
        finally:
            f.close()
        if temporary and sys.platform == "win32":
            os.unlink(path_u)
            self.notify(path, self.inotify.IN_DELETE)
        fileutil.flush_volume(path_u)
        self.notify(path, self.inotify.IN_CLOSE_WRITE)

        if temporary:
            d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_disappeared'),
                                                                 previously_disappeared + 1))
        else:
            d.addCallback(lambda ign: self.upload_dirnode.get(name_u))
            d.addCallback(download_to_data)
            d.addCallback(lambda actual_data: self.failUnlessReallyEqual(actual_data, data))
            d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_succeeded'),
                                                                 previously_uploaded + 1))

        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_queued'), 0))
        return d

    def test_alice_bob(self):
        d = self.setup_alice_and_bob()
        def get_results(result):
            # XXX
            self.alice_collective_dir, self.alice_upload_dircap, self.alice_magicfolder, self.bob_collective_dircap, self.bob_upload_dircap, self.bob_magicfolder = result
        d.addCallback(get_results)

        def Alice_write_a_file(result):
            print "Alice writes a file\n"
            self.file_path = abspath_expanduser_unicode(u"file1", base=self.alice_magicfolder._local_dir)
            fileutil.write(self.file_path, "meow, meow meow. meow? meow meow! meow.")
            self.magicfolder = self.alice_magicfolder
            self.notify(to_filepath(self.file_path), self.inotify.IN_CLOSE_WRITE)

        d.addCallback(Alice_write_a_file)

        def Alice_wait_for_upload(result):
            print "Alice waits for an upload\n"
            d2 = defer.Deferred()
            self.alice_magicfolder.set_processed_callback(d2.callback, ignore_count=0)
            return d2
        d.addCallback(Alice_wait_for_upload)
        def Alice_prepare_for_alice_stats(result):
            self.stats_provider = self.alice_magicfolder._client.stats_provider
        d.addCallback(Alice_prepare_for_alice_stats)
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_succeeded'), 1))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.files_uploaded'), 1))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_queued'), 0))
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.directories_created'), 0))

        def Bob_wait_for_download(result):
            print "Bob waits for a download\n"
            d2 = defer.Deferred()
            self.bob_magicfolder.set_download_callback(d2.callback, ignore_count=0)
            return d2
        d.addCallback(Bob_wait_for_download)
        def Bob_prepare_for_stats(result):
            self.stats_provider = self.bob_magicfolder._client.stats_provider
        d.addCallback(Bob_prepare_for_stats)
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_downloaded'), 1))

        # test deletion of file behavior
        def Alice_delete_file(result):
            print "Alice deletes the file!\n"
            os.unlink(self.file_path)
            self.notify(to_filepath(self.file_path), self.inotify.IN_DELETE)

            return None
        d.addCallback(Alice_delete_file)
        d.addCallback(Alice_wait_for_upload)
        d.addCallback(Alice_prepare_for_alice_stats)
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_succeeded'), 2)) # XXX ?
        d.addCallback(Bob_wait_for_download)
        d.addCallback(Bob_prepare_for_stats)
        d.addCallback(lambda ign: self.failUnlessReallyEqual(self._get_count('magic_folder.objects_downloaded'), 2)) # XXX ?

        def cleanup_Alice_and_Bob(result):
            d = defer.succeed(None)
            d.addCallback(lambda ign: self.alice_magicfolder.finish(for_tests=True))
            d.addCallback(lambda ign: self.bob_magicfolder.finish(for_tests=True))
            d.addCallback(lambda ign: result)
            return d
        d.addCallback(cleanup_Alice_and_Bob)
        return d

class MockTest(MagicFolderTestMixin, unittest.TestCase):
    """This can run on any platform, and even if twisted.internet.inotify can't be imported."""

    def setUp(self):
        MagicFolderTestMixin.setUp(self)
        self.inotify = fake_inotify

    def notify(self, path, mask):
        self.magicfolder._notifier.event(path, mask)

    def test_errors(self):
        self.set_up_grid()

        errors_dir = abspath_expanduser_unicode(u"errors_dir", base=self.basedir)
        os.mkdir(errors_dir)
        not_a_dir = abspath_expanduser_unicode(u"NOT_A_DIR", base=self.basedir)
        fileutil.write(not_a_dir, "")
        magicfolderdb = abspath_expanduser_unicode(u"magicfolderdb", base=self.basedir)
        doesnotexist  = abspath_expanduser_unicode(u"doesnotexist", base=self.basedir)

        client = self.g.clients[0]
        d = client.create_dirnode()
        def _check_errors(n):
            self.failUnless(IDirectoryNode.providedBy(n))
            upload_dircap = n.get_uri()
            readonly_dircap = n.get_readonly_uri()

            self.shouldFail(AssertionError, 'nonexistent local.directory', 'there is no directory',
                            MagicFolder, client, upload_dircap, '', doesnotexist, magicfolderdb, inotify=fake_inotify)
            self.shouldFail(AssertionError, 'non-directory local.directory', 'is not a directory',
                            MagicFolder, client, upload_dircap, '', not_a_dir, magicfolderdb, inotify=fake_inotify)
            self.shouldFail(AssertionError, 'bad upload.dircap', 'does not refer to a directory',
                            MagicFolder, client, 'bad', '', errors_dir, magicfolderdb, inotify=fake_inotify)
            self.shouldFail(AssertionError, 'non-directory upload.dircap', 'does not refer to a directory',
                            MagicFolder, client, 'URI:LIT:foo', '', errors_dir, magicfolderdb, inotify=fake_inotify)
            self.shouldFail(AssertionError, 'readonly upload.dircap', 'is not a writecap to a directory',
                            MagicFolder, client, readonly_dircap, '', errors_dir, magicfolderdb, inotify=fake_inotify)

            def _not_implemented():
                raise NotImplementedError("blah")
            self.patch(magic_folder, 'get_inotify_module', _not_implemented)
            self.shouldFail(NotImplementedError, 'unsupported', 'blah',
                            MagicFolder, client, upload_dircap, '', errors_dir, magicfolderdb)
        d.addCallback(_check_errors)
        return d


class RealTest(MagicFolderTestMixin, unittest.TestCase):
    """This is skipped unless both Twisted and the platform support inotify."""

    def setUp(self):
        MagicFolderTestMixin.setUp(self)
        self.inotify = magic_folder.get_inotify_module()

    def notify(self, path, mask):
        # Writing to the filesystem causes the notification.
        pass

try:
    magic_folder.get_inotify_module()
except NotImplementedError:
    RealTest.skip = "Magic Folder support can only be tested for-real on an OS that supports inotify or equivalent."
