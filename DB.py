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
        cursor.execute("SELECT * FROM users ORDER BY user_name")
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
                                     title VARCHAR(100),
                                     content VARCHAR(10000),
                                     choices VARCHAR(1000),
                                     correct_choice VARCHAR(100),
                                     user_id INTEGER 
                             )''')
        cursor.close()
        self.connection.commit()

    def get_connection(self):
        return self.connection

    def index(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        return rows[-1][0]

    def insert(self, title, content, choices, correct, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO tasks
                          (title, content, choices, correct_choice, user_id) 
                          VALUES (?,?,?,?,?)''', (title, content, choices, correct, user_id,))
        cursor.close()
        self.connection.commit()

    def update(self, title, content, choices, correct, task_id):
        cursor = self.connection.cursor()
        cursor.execute('UPDATE tasks SET title=?, content=?, choices=?, correct_choice=? WHERE id=?',
                       (title, content, choices, correct, task_id,))
        cursor.close()
        self.connection.commit()

    def get(self, title):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tasks WHERE title = ?", (title,))
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


class ScoresModel:
    def __init__(self, connection):
        self.connection = connection.get_connection()

    def init_table(self):
        cursor = self.connection.cursor()
        # cursor.execute('DROP TABLE IF EXISTS scores')
        cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                     num_tasks INTEGER,
                                     num_correct INTEGER,
                                     task_id INTEGER
                                     )''')
        cursor.close()
        self.connection.commit()

    def get_connection(self):
        return self.connection

    def insert(self, num_tasks, num_correct, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO scores
                          (num_tasks, num_correct, task_id)
                          VALUES (?,?,?)''', (str(num_tasks), str(num_correct), str(task_id)))
        cursor.close()
        self.connection.commit()

    def get_all(self, task_id=None):
        cursor = self.connection.cursor()
        if task_id:
            cursor.execute("SELECT * FROM scores WHERE task_id = ?", (str(task_id),))
        else:
            cursor.execute("SELECT * FROM scores")
        rows = cursor.fetchall()
        return rows

    def update(self, task_id, k):
        cursor = self.connection.cursor()
        cursor.execute('UPDATE scores SET num_correct=? WHERE task_id=?', (str(k), str(task_id)))
        cursor.close()
        self.connection.commit()

    def delete(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM scores WHERE task_id = ?''', (str(task_id),))
        cursor.close()
        self.connection.commit()


class ProgressModel:
    def __init__(self, connection):
        self.connection = connection.get_connection()

    def init_table(self):
        cursor = self.connection.cursor()
        # cursor.execute('DROP TABLE IF EXISTS progress')
        cursor.execute('''CREATE TABLE IF NOT EXISTS files
                                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        answers VARCHAR(10000),
                                        correct VARCHAR(10000),
                                        task_id INTEGER
                                        )''')
        cursor.close()
        self.connection.commit()

    def get_connection(self):
        return self.connection

    def insert(self, answers, correct, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO progress
                          (answers, correct, task_id)
                          VALUES (?,?,?)''', (str(answers), str(correct), str(task_id)))
        cursor.close()
        self.connection.commit()

    def get_all(self, task_id=None):
        cursor = self.connection.cursor()
        if task_id:
            cursor.execute("SELECT * FROM progress WHERE task_id = ?", (str(task_id),))
        else:
            cursor.execute("SELECT * FROM progress")
        rows = cursor.fetchall()
        return rows

    def update(self, answer, correct, id):
        cursor = self.connection.cursor()
        cursor.execute('UPDATE progress SET answers=?, correct=? WHERE task_id = ?', (answer, correct, str(id),))
        cursor.close()
        self.connection.commit()

    def delete(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM progress WHERE task_id = ?''', (str(task_id),))
        cursor.close()
        self.connection.commit()


class Files:
    def __init__(self, connection):
        self.connection = connection.get_connection()

    def init_table(self):
        cursor = self.connection.cursor()
        # cursor.execute('DROP TABLE IF EXISTS progress')
        cursor.execute('''CREATE TABLE IF NOT EXISTS files
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                     file BLOB,
                                     task_id INTEGER
                                     )''')
        cursor.close()
        self.connection.commit()

    def get_connection(self):
        return self.connection

    def insert(self, file, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO files
                          (file, task_id)
                          VALUES (?,?)''', ((file,), str(task_id)))
        cursor.close()
        self.connection.commit()

    def get_all(self, task_id=None):
        cursor = self.connection.cursor()
        if task_id:
            cursor.execute("SELECT * FROM files WHERE task_id = ?", (str(task_id),))
        else:
            cursor.execute("SELECT * FROM files")
        rows = cursor.fetchall()
        return rows

    def update(self, answer, correct, id):
        cursor = self.connection.cursor()
        cursor.execute('UPDATE progress SET answers=?, correct=? WHERE task_id = ?', (answer, correct, str(id),))
        cursor.close()
        self.connection.commit()

    def delete(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM files WHERE task_id = ?''', (str(task_id),))
        cursor.close()
        self.connection.commit()
