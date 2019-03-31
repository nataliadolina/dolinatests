import sqlite3
import hashlib


class DB:
    def __init__(self):
        conn = sqlite3.connect('news.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection.get_connection()

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def get_connection(self):
        return self.connection

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        password_hash = hashlib.sha224(password_hash.encode('utf-8')).hexdigest()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?", (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        password_hash = hashlib.sha224(password_hash.encode('utf-8')).hexdigest()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()

    def delete(self):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM users''')


class TasksModel:
    def __init__(self, connection):
        self.connection = connection.get_connection()

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                     content VARCHAR(100),
                                     choices VARCHAR(1000),
                                     user_id INTEGER 
                             )''')
        cursor.close()
        self.connection.commit()

    def get_connection(self):
        return self.connection

    def insert(self, content, choices, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO tasks
                          (content,choices, user_id) 
                          VALUES (?,?,?)''', (content, choices, user_id))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (str(user_id),))
        else:
            cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM tasks WHERE id = ?''', (str(news_id),))
        cursor.close()
        self.connection.commit()
