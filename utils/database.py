import os
import sqlite3
from contextlib import contextmanager

DB_DEFAULTS = {
    'BOT_TOKEN': None,
}


class DB:
    @staticmethod
    @contextmanager
    def cursor():
        conn = sqlite3.connect('database.db')
        conn.row_factory = DB.dict_factory
        try:
            yield conn.cursor()
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    @staticmethod
    def clean_db():
        DB.__drop_tables()
        DB.__create_tables()
        DB.__seed_tables()

    @staticmethod
    def __drop_tables():
        with DB.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS settings")
            cur.execute("DROP TABLE IF EXISTS roles")

    @staticmethod
    def __create_tables():
        with DB.cursor() as cur:
            cur.execute("CREATE TABLE settings ("
                        "key text UNIQUE PRIMARY KEY,"
                        "value text"
                        ")")
            cur.execute("CREATE TABLE roles ("
                        "guild_id int,"
                        "discord_role_id int,"
                        "permission_level int"
                        ")")

    @staticmethod
    def __seed_tables():
        with DB.cursor() as cur:
            pass

    @staticmethod
    def get_setting(key, default=None):
        with DB.cursor() as cur:
            cur.execute("SELECT * from settings where key=?", (key,))
            value = cur.fetchone()
            if value:
                return value['value']
            elif key in DB_DEFAULTS:
                return DB_DEFAULTS[key]
            else:
                return default

    @staticmethod
    def set_setting(key, value):
        with DB.cursor() as cur:
            cur.execute("INSERT INTO settings(key, value) VALUES"
                        "(:key, :value) "
                        "ON CONFLICT(key) DO UPDATE SET value=:value;", {'key': key, 'value': value})


if not os.path.exists('database.db'):
    DB.clean_db()
