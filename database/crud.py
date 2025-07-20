import sqlite3
from threading import Lock
from datetime import datetime
from typing import List, Tuple, Optional
from .models import User, SentImage

db_lock = Lock()

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect('users.db', check_same_thread=False)

def init_db():
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                         user_id INTEGER PRIMARY KEY,
                         username TEXT)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS sent_images (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         user_id INTEGER NOT NULL,
                         file_id TEXT NOT NULL,
                         date INTEGER NOT NULL,
                         FOREIGN KEY(user_id) REFERENCES users(user_id))''')
        
        conn.commit()
        conn.close()

def add_user(user: User) -> bool:
    with db_lock:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                '''INSERT INTO users (user_id, username) 
                   VALUES (?, ?)''',
                (user.user_id, user.username)
            )
            
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"{datetime.now():%Y-%m-%d %H:%M} Добавлен новый пользователь: {user.user_id}")
                return True
        except sqlite3.Error as e:
            print(f"{datetime.now():%Y-%m-%d %H:%M} Ошибка при добавлении пользователя: {e}")
            return []
        finally:
            if conn:
                conn.close()

def get_all_users() -> List[User]:
    with db_lock:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, username FROM users')
            return [User(*row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Ошибка получения пользователей: {e}")
            return []
        finally:
            if conn:
                conn.close()

def add_sent_image(user_id: int, file_id: str) -> bool:
    with db_lock:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO sent_images (user_id, file_id, date) VALUES (?, ?, ?)',
                (user_id, file_id, int(datetime.now().timestamp()))
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка добавления изображения {file_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()

def get_sent_images(user_id: int) -> List[SentImage]:
    with db_lock:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT user_id, file_id, date FROM sent_images WHERE user_id = ?',
                (user_id,)
            )
            return [SentImage(*row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Ошибка получения изображений: {e}")
            return []
        finally:
            if conn:
                conn.close()

def get_users_with_images() -> List[Tuple[User, SentImage]]:
    with db_lock:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''SELECT u.user_id, u.username, s.file_id, s.date 
                             FROM users u JOIN sent_images s ON u.user_id = s.user_id''')
            return [(User(row[0], row[1]), SentImage(row[0], row[2], row[3])) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Ошибка получения данных: {e}")
            return []
        finally:
            if conn:
                conn.close()

def get_users_without_images() -> List[User]:
    with db_lock:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''SELECT u.user_id, u.username FROM users u
                             WHERE NOT EXISTS (
                                 SELECT 1 FROM sent_images s WHERE s.user_id = u.user_id
                             )''')
            return [User(*row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Ошибка получения пользователей без изображений: {e}")
            return []
        finally:
            if conn:
                conn.close()

def get_user_count() -> int:
    with db_lock:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Ошибка получения количества пользователей: {e}")
            return 0
        finally:
            if conn:
                conn.close()
