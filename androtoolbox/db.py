from .adb import adb

SQLITE_BIN = '/data/local/tmp/bin/sqlite3'


def build_db_path(package, db):
    """
    Build the full device path for a package's database

    :param package: The package's name
    :param db: The database's name
    """
    if db.endswith('.db'):
        db = db.rsplit('.', 1)[0]
    return '/data/data/{package}/databases/{db}.db'.format(package=package, db=db)


def execute(db_path, statement):
    """
    Execute an sqlite3 statement on a DB

    :param db_path: The DB to operate on.
    :param statement: The statement to execute
    """
    if not adb.file_exists(db_path, use_su=True):
        raise ValueError("DB file %s does not exist" % db_path)
    cmd = r'%s %s \"%s\"' % (SQLITE_BIN, db_path, statement)
    return adb.shell(cmd, use_su=True)


class Database(object):
    """
    A wrapper class for some useful DB operations.
    """
    def __init__(self, package, database):
        self.package = package
        self.database = database
        self.db_path = build_db_path(package, database)

    def execute(self, statement):
        """
        Execute an sqlite3 statement on a DB and return the raw result

        :param statement: The SQL statement to execute
        """
        return execute(self.db_path, statement).strip()

    @property
    def tables(self):
        return self.execute('.tables').strip().split()

    def schema(self, schema_pattern=None):
        if schema_pattern:
            stmt = ".schema %s" % schema_pattern
        else:
            stmt = '.schema'

        return self.execute(stmt).splitlines()

    def query(self, statement):
        """
        Execute the query statement and return a formatted response where each raw from the response will be
        a list in the list of rows

        :param statement: The SQL statement to execute
        """
        rows = self.execute(statement).splitlines()
        return [row.split('|') for row in rows]
