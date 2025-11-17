import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from utils.logger import logger
from utils.utils import populate_initial_public_skills


class StorageManager:
    def __init__(self, db_name='app.db'):
        self.db_name = db_name
        self.init_tables()
        populate_initial_public_skills(self, "buplic_skills_manager")

    def get_connection(self):
        """Создает соединение, которое возвращает словари."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row 
        return conn

    def init_tables(self):
        with self.get_connection() as conn:
            # Таблица пользователей
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Таблица саммарайзов чатов
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    summarize TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Таблица бзеров в чатах
            conn.execute('''
            CREATE TABLE IF NOT EXISTS user_chats (
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, chat_id),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
            )
            ''')

            # Таблица промптов (навыков)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    content TEXT NOT NULL,          -- Это сам промпт
                    max_tokens INTEGER DEFAULT 2000,
                    created_by INTEGER NOT NULL,
                    is_public BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')

            # Связующая таблица для "сохраненных" навыков
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_prompts (
                    user_id INTEGER,
                    prompt_id INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, prompt_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (prompt_id) REFERENCES prompts (id)
                )
            ''')
            conn.commit()

    def get_user_id(self, username: str) -> int:
        """
        Находит пользователя по username или создает нового, 
        в любом случае возвращает user_id.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            user_row = cursor.fetchone()
            
            if user_row:
                logger.info(f"Найден пользователь '{username}' с ID: {user_row['id']}")
                return user_row['id']

            return self.add_user(username)

    def add_user(self, username):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                logger.warning(f"Пользователь '{username}' уже существует.")
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                return cursor.fetchone()['id']
    
    # Создание чата
    def add_chat(self, name: str, summarize: str | None = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO chats (name, summarize) VALUES (?, ?)', (name, summarize))
            conn.commit()
            return cursor.lastrowid

    def add_user_to_chat(self, user_id: int, chat_id: int):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR IGNORE INTO user_chats (user_id, chat_id)
                VALUES (?, ?)
            ''', (user_id, chat_id))
            conn.commit()

    # Получить все чаты, где состоит пользователь
    def get_user_chats(self, user_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.name
                FROM chats c
                JOIN user_chats uc ON uc.chat_id = c.id
                WHERE uc.user_id = ?
                ORDER BY c.created_at DESC
            ''', (user_id,))
            return set(cursor.fetchall())
        

    def get_chat_id(self, name: str) -> int:
        """
        Находит пользователя по username или создает нового, 
        в любом случае возвращает user_id.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM chats WHERE name = ?', (name,))
            chat_row = cursor.fetchone()
            if chat_row:
                logger.info(f"Найден чат '{name}' с ID: {chat_row['id']}")
                return chat_row['id']
            return self.add_chat(name)
        

    def get_chats_created_after(self, created_after: datetime | str, chat_name: str): 
        with self.get_connection() as conn: 
            cursor = conn.cursor() 
            if isinstance(created_after, datetime): 
                ts = created_after.strftime('%Y-%m-%d %H:%M:%S') 
            else: 
                ts = created_after 
            cursor.execute(''' SELECT * FROM chats WHERE created_at > ? AND name == ? ORDER BY created_at ASC ''', (ts, chat_name)) 
            return cursor.fetchall()

    def add_prompt(self, title, content, created_by, description=None, is_public=False, max_tokens=2000):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO prompts (title, description, content, created_by, is_public, max_tokens)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, description, content, created_by, is_public, max_tokens))
            conn.commit()
            return cursor.lastrowid

    def link_prompt_to_user(self, user_id, prompt_id):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR IGNORE INTO user_prompts (user_id, prompt_id)
                VALUES (?, ?)
            ''', (user_id, prompt_id))
            conn.commit()

    def get_user_prompts(self, user_id):
        """Получает все промпты, которые 'сохранил' пользователь."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.* FROM prompts p
                JOIN user_prompts up ON p.id = up.prompt_id
                WHERE up.user_id = ?
            ''', (user_id,))
            return cursor.fetchall()

    def get_public_prompts(self):
        """Получает все публичные промпты."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM prompts WHERE is_public = True')
            return cursor.fetchall()

    def get_prompt_for_user(self, user_id: int, prompt_id: int):
        """
        Получает 1 промпт по ID. 
        Возвращает его, ТОЛЬКО если он публичный ИЛИ сохранен у пользователя.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.* FROM prompts p
                LEFT JOIN user_prompts up ON p.id = up.prompt_id AND up.user_id = ?
                WHERE p.id = ? 
                AND (p.is_public = True OR up.user_id IS NOT NULL)
            ''', (user_id, prompt_id))
            return cursor.fetchone()

storage_manager = StorageManager()