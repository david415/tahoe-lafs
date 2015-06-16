
# do not import any allmydata modules at this level. Do that from inside
# individual functions instead.
from twisted.python import usage, failure
from allmydata.scripts.cli import FilesystemOptions, BaseOptions, CreateAliasOptions
from allmydata.util.encodingutil import argv_to_unicode

class CreateMagicFolderOptions(BaseOptions):
    synopsis = "[options] ALIAS[:]"
    description = """Create a new directory and add an alias for it."""
    alias = ''
    description = """
Create a new Magic-Folder.

 tahoe magic-folder create myShareGroup1
"""

    def getSynopsis(self):
        return "Usage: tahoe [global-options] magic-folder create MAGIC"

    def parseArgs(self, *option_args):
        if not option_args:
            raise usage.UsageError("must specify at least a Magic-Folder name")
        else:
            self.alias = argv_to_unicode(option_args[0])
            if self.alias.endswith(u':'):
                self.alias = self.alias[:-1]


class InviteOptions(BaseOptions):
    pass
class JoinOptions(BaseOptions):
    pass

class MagicFolderCommand(BaseOptions):
    subCommands = [
        ["create", None, CreateMagicFolderOptions, "Create a Magic-Folder."],
        ["invite", None, InviteOptions, "Invite someone to a Magic-Folder."],
        ["join", None, JoinOptions, "Join a Magic-Folder."],
    ]

    def postOptions(self):
        if not hasattr(self, 'subOptions'):
            raise usage.UsageError("must specify a subcommand")
        synopsis = "COMMAND"

    def getUsage(self, width=None):
        t = BaseOptions.getUsage(self, width)
        t += """\

Please run e.g. 'tahoe magic-folder create --help' for more details on each
subcommand.
"""
        return t

def create(options):
    from allmydata.scripts import tahoe_add_alias
    rc = tahoe_add_alias.create_alias(options, alias_file="magic-folder-aliases")
    return rc

def invite(options):
    pass

def join(options):
    pass

subDispatch = {
    "create": create,
    "invite": invite,
    "join": join,
}

subCommands = [
    ["magic-folder", None, MagicFolderCommand, "magic-folder subcommands: use 'tahoe magic-folder' for a list."],
]

def do_magic_folder(options):
    so = options.subOptions
    so.stdout = options.stdout
    so.stderr = options.stderr
    f = subDispatch[options.subCommand]
    return f(so)

dispatch = {
    "magic-folder": do_magic_folder,
    }
