import sqlite3
import hashlib
import os

DB_NAME = 'users.db'
AVATAR_FOLDER = 'static/avatars'


def init_db():
    os.makedirs(AVATAR_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, email TEXT, full_name TEXT, avatar TEXT)''')
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password, email=None, full_name=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO users (username, password, email, full_name, avatar) VALUES (?, ?, ?, ?, ?)''',
                       (username, hash_password(password), email, full_name, 'default_avatar.png'))
        conn.commit()
        return True, "Регистрация успешна!"
    except sqlite3.IntegrityError:
        return False, "Пользователь с таким именем уже существует"
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''SELECT id, username, email, full_name, avatar FROM users WHERE username = ? AND password = ?''',
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    if user:
        return True, {'id': user[0], 'username': user[1], 'email': user[2],
                      'full_name': user[3], 'avatar': user[4]}
    return False, "Неверное имя пользователя или пароль"


def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''SELECT id, username, email, full_name, avatar FROM users WHERE id = ?''', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {'id': user[0], 'username': user[1], 'email': user[2],
                'full_name': user[3], 'avatar': user[4]}
    return None


def update_user_profile(user_id, email=None, full_name=None, avatar_filename=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT email, full_name, avatar FROM users WHERE id = ?', (user_id,))
    current = cursor.fetchone()
    new_email = email if email else current[0]
    new_full_name = full_name if full_name else current[1]
    new_avatar = avatar_filename if avatar_filename else current[2]
    cursor.execute('''UPDATE users SET email = ?, full_name = ?, avatar = ? WHERE id = ?''',
                   (new_email, new_full_name, new_avatar, user_id))
    conn.commit()
    conn.close()
    return True
