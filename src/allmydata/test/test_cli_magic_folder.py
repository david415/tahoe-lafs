import os.path
from twisted.trial import unittest
import urllib
from allmydata.util import fileutil
from allmydata.scripts.common import get_aliases
from allmydata.scripts import cli, runner
from allmydata.test.no_network import GridTestMixin
from allmydata.util.encodingutil import quote_output, get_io_encoding
from .test_cli import CLITestMixin

class CreateMagicFolder(GridTestMixin, CLITestMixin, unittest.TestCase):

    def test_create(self):
        self.basedir = "cli/MagicFolder/create"
        self.set_up_grid()
        aliasfile = os.path.join(self.get_clientdir(), "private", "magic-folder-aliases")

        d = self.do_cli("magic-folder", "create", "my_magic_folder")

        def _done((rc,stdout,stderr)):
            self.failUnless("Alias 'my_magic_folder' created" in stdout)
            self.failIf(stderr)
            aliases = get_aliases(self.get_clientdir(), aliases_file="magic_folder_aliases")
            self.failUnless("my_magic_folder" in aliases)
            self.failUnless(aliases["my_magic_folder"].startswith("URI:DIR2:"))
        d.addCallback(_done)
        return d
        # XXX more stuff ...
