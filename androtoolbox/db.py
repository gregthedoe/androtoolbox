import os
import re

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


def databases_for_package(package):
    """
    List all available database for a package
    """
    db_glob_path = build_db_path(package, '*')
    db_paths = adb.shell('ls %s' % db_glob_path, use_su=True).strip().split()
    db_names = [os.path.splitext(os.path.basename(db_path))[0] for db_path in db_paths]
    return db_names


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
        """
        Get the schema for the db or a specific table.

        :param schema_pattern: An optional pattern to filter tables
        """
        if schema_pattern:
            stmt = ".schema %s" % schema_pattern
        else:
            stmt = '.schema'

        return self.execute(stmt).splitlines()

    def query(self, statement, expected_fields_number=-1):
        """
        Execute the query statement and return a formatted response where each raw from the response will be
        a list in the list of rows

        :param statement: The SQL statement to execute
        :param expected_fields_number: The number of expected fields, if unknown pass -1
        """
        rows = self.execute(statement).splitlines()
        maxsplit = expected_fields_number - 1 if expected_fields_number > 0 else -1
        return [row.split('|', maxsplit) for row in rows]


class KeyValueTable(object):
    """
    A container for key-value DB tables
    """

    def __init__(self, db, table, key='name', value='value'):
        """
        Initialize the container.

        :param db: The database that contains the Key-Value table.
        :type db: Database
        :param table: The table's name inside the DB
        :param key: The name of the key field in the table
        :param value: The name of the value field in the table
        """
        self.db = db
        self.table = table
        self._key = key
        self._value = value

    def _get_all_as_dict(self):
        query = 'select {key}, {value} from {table}'.format(key=self._key, value=self._value, table=self.table)
        return dict(self.db.query(query, 2))

    def __getitem__(self, item):
        query = r"select {key}, {value} from {table} " \
                r"where {key}='{item}';".format(key=self._key, value=self._value, table=self.table, item=item)
        result = self.db.query(query)
        if not result:
            raise KeyError(item)
        key, value = result[0]
        return value

    def has_key(self, key):
        return key in self

    def __contains__(self, item):
        stmt = "select {key_name} from {table} where {key_name}='{key}';".format(key_name=self._key,
                                                                                 table=self.table,
                                                                                 key=item)
        return self.db.execute(stmt) == item

    def __setitem__(self, key, value):
        if key in self:
            self._update_key(key, value)
        else:
            self._insert_key(key, value)

    def _update_key(self, key, value):
        stmt = "update {table} set {value_name}='{value}' where {key_name}='{key}'".format(table=self.table,
                                                                                           value_name=self._value,
                                                                                           key_value=self._key,
                                                                                           value=value,
                                                                                           key=key)
        self.db.execute(stmt)

    def _insert_key(self, key, value):
        stmt = "insert into {table} ({key_name}, {value_name}) " \
               "values ({key}, {value})".format(table=self.table, key_name=self._key, value_name=self._value,
                                                key=key, value=value)
        self.db.execute(stmt)

    def __getattr__(self, item):
        return getattr(self._get_all_as_dict(), item)

    def items_by_pattern(self, key_pattern):
        """
        Get all items filtered by a key pattern.

        :param key_pattern: The key pattern (a regex string)
        """
        items = self._get_all_as_dict().items()
        filtered_items = [(k, v) for k, v in items if re.search(key_pattern, k)]
        return filtered_items
