class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cur = self.connection.cursor()
        cur.execute(f"""CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             username VARCHAR(50),
                             password_hash VARCHAR(128)
                             )""")
        cur.close()
        self.connection.commit()

    def insert(self, username, password_hash):
        cur = self.connection.cursor()
        cur.execute(f'''INSERT INTO users(username, password_hash, is_admin)
                    VALUES (?, ?, 0)''', (username, password_hash))
        cur.close()
        self.connection.commit()

    def get(self, values=None, cond=None):
        cur = self.connection.cursor()
        if values is None:
            values = "*"
        if cond is None:
            cond = ""
        cur.execute(f"SELECT {values} FROM users {cond}")
        return cur

    def get_all(self):
        cur = self.connection.cursor()
        cur.execute(f"SELECT * FROM users")
        rows = cur.fetchall()
        return rows

    def exists(self, username, password_hash=None):
        cur = self.connection.cursor()
        if password_hash is None:
            cur.execute(f'SELECT * FROM users WHERE username = ?', (username, ))
            row = cur.fetchone()
        else:
            cur.execute(f"""SELECT * FROM users WHERE 
                        username = ? AND password_hash = ?""", (username, password_hash))
            row = cur.fetchone()
        return (True, row[0]) if row else (False,)

    def other_commands(self, command):
        cur = self.connection.cursor()
        cur.execute(command)
        return cur
