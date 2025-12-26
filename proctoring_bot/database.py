import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_name="survey.db", config_loader=None):
        self.db_name = db_name
        self.config_loader = config_loader
        self.init_database()

    def init_database(self):
        """Создает таблицу для ответов"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Создаем таблицу с базовыми полями и полями для вопросов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Если есть конфигурация, добавляем поля для вопросов
        if self.config_loader:
            for question in self.config_loader.questions:
                try:
                    cursor.execute(f'''
                        ALTER TABLE user_responses 
                        ADD COLUMN {question['id']} TEXT
                    ''')
                except sqlite3.OperationalError:
                    pass  # Поле уже существует

        conn.commit()
        conn.close()

    def save_answer(self, user_id, question_id, answer, user_info=None):
        """Сохраняет ответ на вопрос"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Проверяем, есть ли запись пользователя
        cursor.execute("SELECT * FROM user_responses WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()

        if existing:
            # Обновляем существующую запись
            cursor.execute(f'''
                UPDATE user_responses 
                SET {question_id} = ?, updated_at = ?
                WHERE user_id = ?
            ''', (answer, datetime.now(), user_id))
        else:
            # Создаем новую запись
            if user_info:
                cursor.execute('''
                    INSERT INTO user_responses (user_id, username, first_name)
                    VALUES (?, ?, ?)
                ''', (user_id, user_info.get('username'), user_info.get('first_name')))

            # Обновляем поле с ответом
            cursor.execute(f'''
                UPDATE user_responses 
                SET {question_id} = ?, updated_at = ?
                WHERE user_id = ?
            ''', (answer, datetime.now(), user_id))

        conn.commit()
        conn.close()

    def get_user_responses(self, user_id):
        """Получает все ответы пользователя"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user_responses WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return {}

    def is_completed(self, user_id):
        """Проверяет, полностью ли заполнена анкета"""
        responses = self.get_user_responses(user_id)
        if not responses:
            return False

        # Проверяем все обязательные вопросы
        if self.config_loader:
            for question in self.config_loader.questions:
                if question.get('required', False):
                    answer = responses.get(question['id'])
                    if not answer or answer == '':
                        return False
        return True

    def delete_user_responses(self, user_id):
        """Удаляет все ответы пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM user_responses WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()