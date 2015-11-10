
import sys

from allmydata.util.dbutil import get_db, DBError


# magic-folder db schema version 1
SCHEMA_v1 = """
CREATE TABLE version
(
 version INTEGER  -- contains one row, set to 1
);

CREATE TABLE parents
(
 child_uri                      VARCHAR(91) PRIMARY KEY, -- URI:DIR2-CHK:
 parent_uri                     VARCHAR(91),             -- URI:DIR2-CHK:
 unique(child_uri, parent_uri),
);

CREATE TABLE snapshots
(
 uri                     VARCHAR(91) PRIMARY KEY, -- URI:DIR2-CHK:
 content_uri             VARCHAR(91),             -- URI:CHK:
 mtime                   NUMBER,                  -- ST_MTIME
 ctime                   NUMBER,                  -- ST_CTIME
);

CREATE TABLE local_files
(
 path                   VARCHAR(1024) PRIMARY KEY, -- UTF-8 filename relative to local magic folder dir
 size                   INTEGER,                   -- ST_SIZE, or NULL if the file has been deleted
 mtime                  NUMBER,                    -- ST_MTIME
 ctime                  NUMBER,                    -- ST_CTIME
 current_snapshot_uri   VARCHAR(256) UNIQUE,       -- URI:DIR2-CHK:
);
"""


def get_magicfolderdb(dbfile, stderr=sys.stderr,
                      create_version=(SCHEMA_v1, 1), just_create=False):
    # Open or create the given backupdb file. The parent directory must
    # exist.
    try:
        (sqlite3, db) = get_db(dbfile, stderr, create_version,
                               just_create=just_create, dbname="magicfolderdb")
        if create_version[1] in (1, 2):
            return MagicFolderDB(sqlite3, db)
        else:
            print >>stderr, "invalid magicfolderdb schema version specified"
            return None
    except DBError, e:
        print >>stderr, e
        return None


class MagicFolderDB(object):
    VERSION = 1

    def __init__(self, sqlite_module, connection):
        self.sqlite_module = sqlite_module
        self.connection = connection
        self.cursor = connection.cursor()

    def check_file_db_exists(self, relpath_u):
        """I will tell you if a given file has an entry in my database or not
        by returning True or False.
        """
        c = self.cursor
        c.execute("SELECT size,mtime,ctime"
                  " FROM local_files"
                  " WHERE path=?",
                  (path,))
        row = self.cursor.fetchone()
        if not row:
            return False
        else:
            return True

    def get_all_relpaths(self):
        """
        Retrieve a set of all relpaths of files that have had an entry in magic folder db
        (i.e. that have been downloaded at least once).
        """
        self.cursor.execute("SELECT path FROM local_files")
        rows = self.cursor.fetchall()
        return set([r[0] for r in rows])

    def is_new_file(self, pathinfo, relpath_u):
        """
        Returns true if the file's current pathinfo (size, mtime, and ctime) has
        changed from the pathinfo previously stored in the db.
        """
        c = self.cursor
        c.execute("SELECT size, mtime, ctime"
                  " FROM local_files"
                  " WHERE path=?",
                  (relpath_u,))
        row = self.cursor.fetchone()
        if not row:
            return True
        if not pathinfo.exists and row[0] is None:
            return False
        return (pathinfo.size, pathinfo.mtime, pathinfo.ctime) != row

    def put_parent(self, child_uri, parent_uri):
        """
        Put a parents table entry into the db.
        """

    def put_snapshot(self, snapshot_uri, content_uri, parents):
        """
        Given the snapshot fields: snapshot URI, content URI and list of parent URIs
        persist to db.
        """

    def get_snapshot(self, uri):
        """
        Given a snapshot URI, retreive a snapshot object
        consisting of a dictionary with the following keys:
           - content: a URI string; empty string if deletion.
           - parents: a list of URI strings; empty list if no parents.
        Returns None if URI is not in the db.
        """
        c = self.cursor
        c.execute("SELECT content_uri, mtime, ctime FROM snapshots WHERE uri=?", (uri,))
        row = self.cursor.fetchone()
        if not row:
            return None
        content_uri, mtime, ctime = row[0]
        c.execute("SELECT parent_uri from parents where child_uri=?", (uri,))
        parents = self.cursor.fetchall()
        snapshot = {
            "content": content_uri,
            "mtime": mtime,
            "ctime": ctime,
            "parents": parents
        }
        return snapshot
