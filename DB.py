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
        cursor.execute('DROP TABLE IF EXISTS tasks')
        cursor.execute('''CREATE TABLE IF NOT EXISTS task
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                     hints VARCHAR(10000) DEFAULT NULL,
                                     title VARCHAR(100),
                                     content VARCHAR(10000),
                                     choices VARCHAR(1000),
                                     correct_choice VARCHAR(100)
                             )''')
        cursor.close()
        self.connection.commit()

    def get_connection(self):
        return self.connection

    def index(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM task")
        rows = cursor.fetchall()
        return rows[-1][0]

    def insert(self, title, content, choices, correct):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO task
                          (title, content, choices, correct_choice) 
                          VALUES (?,?,?,?)''', (title, content, choices, correct))
        cursor.close()
        self.connection.commit()

    def update(self, title, content, choices, correct, task_id):
        cursor = self.connection.cursor()
        cursor.execute('UPDATE task SET title=?, content=?, choices=?, correct_choice=? WHERE id=?',
                       (title, content, choices, correct, task_id,))
        cursor.close()
        self.connection.commit()

    def get(self, id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM task WHERE id = ?", (id,))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM task")
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM task WHERE id = ?''', (str(news_id),))
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
                                     task_id INTEGER,
                                     user_id INTEGER
                                     )''')
        cursor.close()
        self.connection.commit()

    def get_connection(self):
        return self.connection

    def insert(self, num_tasks, num_correct, task_id, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO scores
                          (num_tasks, num_correct, task_id, user_id)
                          VALUES (?,?,?,?)''', (str(num_tasks), str(num_correct), str(task_id), str(user_id)))
        cursor.close()
        self.connection.commit()

    def get_all(self, task_id=None, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM scores WHERE user_id=? AND task_id=?", (str(user_id), str(task_id)))
        else:
            cursor.execute("SELECT * FROM scores")
        rows = cursor.fetchall()
        return rows

    def update(self, task_id, k, user_id):
        cursor = self.connection.cursor()
        cursor.execute('UPDATE scores SET num_correct=? WHERE task_id=? AND user_id=?',
                       (str(k), str(task_id), str(user_id)))
        cursor.close()
        self.connection.commit()

    def delete(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM scores WHERE task_id = ?''', (str(task_id),))
        cursor.close()
        self.connection.commit()


class ProgresssModel:
    def __init__(self, connection):
        self.connection = connection.get_connection()

    def init_table(self):
        cursor = self.connection.cursor()
        # cursor.execute('DROP TABLE IF EXISTS progresss')
        cursor.execute('''CREATE TABLE IF NOT EXISTS progresss
                                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        num_tasks INTEGER,
                                        num_correct INTEGER,
                                        answers VARCHAR(10000),
                                        correct VARCHAR(10000),
                                        task_id INTEGER,
                                        user_id INTEGER
                                        )''')
        cursor.close()
        self.connection.commit()

    def get_connection(self):
        return self.connection

    def insert(self, num_tasks, num_correct, answers, correct, task_id, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO progresss
                          (num_tasks, num_correct, answers, correct, task_id, user_id)
                          VALUES (?,?,?,?,?,?)''',
                       (str(num_tasks), str(num_correct), str(answers), str(correct), str(task_id), str(user_id)))
        cursor.close()
        self.connection.commit()

    def get_all(self, user_id=None, task_id=None):
        cursor = self.connection.cursor()
        if user_id and not task_id:
            cursor.execute("SELECT * FROM progresss WHERE user_id=?", (str(user_id),))
        elif user_id and task_id:
            cursor.execute("SELECT * FROM progresss WHERE task_id=? AND user_id=?", (str(task_id), str(user_id)))
        else:
            cursor.execute("SELECT * FROM progresss")
        rows = cursor.fetchall()
        return rows

    def update(self, num_tasks, num_correct, answer, correct, id, user_id):
        cursor = self.connection.cursor()
        cursor.execute(
            'UPDATE progresss SET num_tasks=?, num_correct=?, answers=?, correct=? WHERE task_id=? AND user_id=?',
            (str(num_tasks), str(num_correct), answer, correct, str(id), str(user_id)))
        cursor.close()
        self.connection.commit()

    def delete(self, task_id, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM progresss WHERE task_id = ? AND user_id=?''', (str(task_id), str(user_id)))
        cursor.close()
        self.connection.commit()


class Files:
    def __init__(self, connection):
        self.connection = connection.get_connection()

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS files')
        cursor.execute('''CREATE TABLE IF NOT EXISTS file
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                     file VARCHAR(10000) DEFAULT NULL,
                                     photo VARCHAR(10000) DEFAULT NULL,
                                     task_id INTEGER
                                     )''')
        cursor.close()
        self.connection.commit()

    def get_connection(self):
        return self.connection

    def insert_file(self, file, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO file
                          (file, task_id)
                          VALUES (?,?)''', (file[0], str(task_id)))
        cursor.close()
        self.connection.commit()

    def insert(self, file, photo, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO file
                                          (file, photo, task_id)
                                          VALUES (?,?,?)''', (file, photo, str(task_id)))
        cursor.close()
        self.connection.commit()

    def get_all(self, task_id=None):
        cursor = self.connection.cursor()
        if task_id:
            cursor.execute("SELECT * FROM file WHERE task_id = ?", (str(task_id),))
        else:
            cursor.execute("SELECT * FROM file")
        rows = cursor.fetchall()
        return rows

    def update_file(self, file, id):
        cursor = self.connection.cursor()
        cursor.execute('UPDATE file SET file=? WHERE task_id = ?', (file, str(id),))
        cursor.close()
        self.connection.commit()

    def update_photo(self, photo, task_id):
        cursor = self.connection.cursor()
        cursor.execute('UPDATE file SET photo=? WHERE task_id = ?', (photo, str(task_id),))
        cursor.close()
        self.connection.commit()

    def delete(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM file WHERE task_id = ?''', (str(task_id),))
        cursor.close()
        self.connection.commit()


class TaskUser:
    def __init__(self, connection):
        self.connection = connection.get_connection()

    def init_table(self):
        cursor = self.connection.cursor()
        # cursor.execute('DROP TABLE IF EXISTS taskuser')
        cursor.execute('''CREATE TABLE IF NOT EXISTS taskuser
                                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        task_id INTEGER,
                                        user_id INTEGER
                                        )''')
        cursor.close()
        self.connection.commit()

    def insert(self, task_id, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO taskuser
                          (task_id, user_id)
                          VALUES (?,?)''', (str(task_id), str(user_id)))
        cursor.close()
        self.connection.commit()

    def get_all(self, id=None):
        cursor = self.connection.cursor()
        if id:
            cursor.execute("SELECT * FROM taskuser WHERE user_id = ?", (str(id),))
        else:
            cursor.execute("SELECT * FROM taskuser")
        rows = cursor.fetchall()
        return rows

    def delete(self, id, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM taskuser WHERE task_id=? AND user_id=?''', (str(id), str(user_id)))
        cursor.close()
        self.connection.commit()
