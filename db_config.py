import sqlite3


class DB_config:

    def __init__(self):
        self.connection = sqlite3.connect('dbase/sys_mon.db')

    def close_connect(self):
        self.connection.close()

    def write(self, cpu, ram, rom):
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS System (
            id INTEGER PRIMARY KEY,
            cpu TEXT NOT NULL,
            ram TEXT NOT NULL,
            rom TEXT NOT NULL
            )
            ''')
            self.connection.commit()
            cursor.execute(
                'INSERT INTO System (cpu, ram, rom) VALUES (?, ?, ?)',
                (
                    cpu,
                    ram,
                    rom
                )
            )
            self.connection.commit()

            return True
        except sqlite3.OperationalError:
            return False

    def read(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM System')
            users = cursor.fetchall()
            return True, users
        except sqlite3.OperationalError:
            return False

    def delete(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute('DROP TABLE System')
            self.connection.commit()
            return True
        except sqlite3.OperationalError:
            return False
