import sqlite3


class DB:
    def __init__(self):
        conn = sqlite3.connect("site_db.db", check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def close_connection(self):
        self.conn.close()
