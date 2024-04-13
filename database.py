import sqlite3
from random import randint

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('data.db', check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY,
        user_length INTEGER,
        user_use_letters INTEGER,
        user_use_digits INTEGER,
        user_use_punctuation INTEGER)
        """)
    except sqlite3.Error as e:
        print(e)

def insert_user(conn, user_id, length, use_letters, use_digits, use_punctuation):
    try:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO Users (user_id, user_length, user_use_letters, user_use_digits, user_use_punctuation)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, length, use_letters, use_digits, use_punctuation))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def update_user_settings(conn, user_id, length, use_letters=True, use_digits=True, use_punctuation=True):
    try:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE Users
        SET user_length = ?,
            user_use_letters = ?,
            user_use_digits = ?,
            user_use_punctuation = ?
        WHERE user_id = ?
        """, (length, use_letters, use_digits, use_punctuation, user_id))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def delete_user(conn, user_id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def get_all_users(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users")
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(e)

def close_connection(conn):
    if conn:
        conn.close()

class UserSettings:
    def __init__(self, user_id):
        self.user_id = user_id
        self._load_settings()

    def _load_settings(self):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_use_letters, user_use_digits, user_use_punctuation, user_length FROM Users WHERE user_id = ?", (self.user_id,))
        settings = cursor.fetchone()
        if settings:
            self.use_letters, self.use_digits, self.use_punctuation, self.user_length = settings
        else:
            # Если пользователь не найден в базе данных, устанавливаем значения по умолчанию
            self.user_length = 8
            self.use_letters = True
            self.use_digits = True
            self.use_punctuation = True