import os
import sqlite3
from contextlib import contextmanager

DB_DEFAULTS = {
    'cur_migration': '0'
}


class DB:
    @staticmethod
    @contextmanager
    def cursor():
        path = '/'.join(__file__.split('/')[:-2])
        conn = sqlite3.connect(path + '/database.db')
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
            cur.execute("DROP TABLE IF EXISTS faculties")
            cur.execute("DROP TABLE IF EXISTS messages")
            cur.execute("DROP TABLE IF EXISTS rules")

    @staticmethod
    def __create_tables():
        with DB.cursor() as cur:
            cur.execute("CREATE TABLE settings ("
                        "key text UNIQUE PRIMARY KEY,"
                        "value text"
                        ")")
            cur.execute("CREATE TABLE faculties ("
                        "role int,"
                        "title text,"
                        "icon text"
                        ")")
            cur.execute("CREATE TABLE messages ("
                        "channel int,"
                        "message int,"
                        "type text"
                        ")")

    @staticmethod
    def __seed_tables():
        with DB.cursor() as cur:
            cur.execute("INSERT INTO faculties (role, title, icon) VALUES "
                        "(898643765198196756, ' None of these', ''), "
                        "(843164248154701830, 'Datorikas fakultāte', 'DF'), "
                        "(843178325366145074, 'Biznesa, vadības un ekonomikas fakultāte', 'BVEF'), "
                        "(843178671086895156, 'Fizikas, matemātikas un optometrijas fakultāte', 'FMOF'), "
                        "(843178899105906688, 'Ģeogrāfijas un Zemes zinātņu fakultāte', 'GZZF'), "
                        "(843179411695075349, 'Ķīmijas fakultāte', 'KF'), "
                        "(843179106786607104, 'Humanitāro zinātņu fakultāte', 'HZF'), "
                        "(843180448497532938, 'Teoloģijas fakultāte', 'TF'), "
                        "(843180597623259147, 'Vēstures un filozofijas fakultāte', 'VFF'), "
                        "(843179777821114395, 'Medicīnas fakultāte', 'MF'), "
                        "(843179307132125244, 'Juridiskā fakultāte', 'JF'), "
                        "(843179947626594314, 'Pedagoģijas, psiholoģijas un mākslas fakultāte', 'PPMF'), "
                        "(843180259565895691, 'Sociālo zinātņu fakultāte', 'SZF'), "
                        "(843177856652804147, 'Bioloģijas fakultāte', 'BF')"
                        )

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

    @staticmethod
    def migrate_db():
        try:
            cur_migration = int(DB.get_setting('cur_migration'))
        except:  # DB has not been initialised yet
            DB.clean_db()
            cur_migration = int(DB.get_setting('cur_migration'))

        if cur_migration < 1:
            DB.set_setting('cur_migration', 1)
            with DB.cursor() as cur:
                cur.execute("INSERT INTO settings VALUES ('cur_migration', 1)")

        if cur_migration < 2:
            DB.set_setting('cur_migration', 2)
            with DB.cursor() as cur:
                cur.execute("CREATE TABLE rules ( "
                            "id int, "
                            "rule text "
                            ")")