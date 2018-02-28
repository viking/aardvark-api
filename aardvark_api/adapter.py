import typing
import sqlite3
from injector import singleton, inject
from aardvark_api.types import Configuration, IntegrityError

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@singleton
class Adapter:
    @inject
    def __init__(self, config: Configuration):
        self.config = config

    def db(self) -> sqlite3.Connection:
        return sqlite3.connect(self.config['db_path'])

    def migrate(self) -> None:
        with self.db() as db:
            cur = db.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS schema_info (version INT)")
            cur.execute("SELECT version FROM schema_info")
            row = cur.fetchone()
            if row is None:
                version = 0
            else:
                version = row[0]

            if version < 1:
                cur.execute("CREATE TABLE packages (id INT PRIMARY KEY, name VARCHAR(50), version VARCHAR(50), filename VARCHAR(255))")
                cur.execute("CREATE UNIQUE INDEX packages_name_version ON packages (name, version)")
                cur.execute("INSERT INTO schema_info (version) VALUES (1)")

    def create(self, table_name, values) -> int:
        cols = ', '.join(values.keys())
        params = ', '.join([':{}'.format(key) for key in values.keys()])
        query = "INSERT INTO {} ({}) VALUES({})".format(table_name, cols, params)
        try:
            with self.db() as db:
                cur = db.cursor()
                cur.execute(query, values)
                return cur.lastrowid
        except sqlite3.IntegrityError as err:
            raise IntegrityError("duplicate record") from err

    def find(self, table_name, conditions=None) -> typing.List[dict]:
        if conditions is None or len(conditions) == 0:
            where = ""
        else:
            where = " WHERE {}".format(' AND '.join(['{0} = :{0}'.format(key) for key in conditions.keys()]))
        with self.db() as db:
            db.row_factory = dict_factory
            cur = db.cursor()
            cur.execute("SELECT * FROM {}{}".format(table_name, where), conditions)
            return curr.fetchall()

