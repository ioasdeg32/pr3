class UnitsModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cur = self.connection.cursor()
        cur.execute(f"""CREATE TABLE IF NOT EXISTS units 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 img  VARCHAR(100),
                                 name VARCHAR(100),
                                 content VARCHAR(1000),
                                 cost INTEGER
                                 )""")
        cur.close()
        self.connection.commit()

    def get(self, values=None, cond=None):
        cur = self.connection.cursor()
        if values is None:
            values = "*"
        if cond is None:
            cond = ""
        cur.execute(f"SELECT {values} FROM units {cond}")
        return cur

    def insert(self, img, name, content, cost):
        cur = self.connection.cursor()
        cur.execute(f'''INSERT INTO units(img, name, content, cost)
                    VALUES (?, ?, ?, ?)''', (img, name, content, cost))
        cur.close()
        self.connection.commit()

    def get_all(self):
        cur = self.connection.cursor()
        cur.execute(f"SELECT * FROM units")
        rows = cur.fetchall()
        return rows

    def delete(self, unit_id):
        cur = self.connection.cursor()
        cur.execute(f"DELETE FROM units WHERE id = ?", (unit_id, ))
        cur.close()
        self.connection.commit()

    def exists(self, name):
        cur = self.connection.cursor()
        cur.execute(f'SELECT * FROM units WHERE name = ?', (name, ))
        row = cur.fetchone()
        if row:
            return True
        else:
            return False
