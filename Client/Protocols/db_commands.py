import logging
import sqlite3
from typing import List, Dict, Any, Optional

from Client.core.config import setup_logger


setup_logger()


class Database:
    def __init__(self, db_name: str = "local_storage.db"):
        """Инициализация подключения к локальной базе данных SQLite."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_name = db_name
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.connect()
        self.logger.info(f'Старт работы с базой {db_name}')

    def connect(self) -> None:
        """Установка соединения с БД."""
        # лучше убрать второй параметр для безопасности
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        # Включаем dict-подобный режим, чтобы получать данные по именам колонок
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        """
        Динамическое создание таблицы.
        schema: словарь вида {"название_колонки": "тип_данных_и_модификаторы"}
        Пример: {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "text": "TEXT"}
        """
        columns = ", ".join([f"{col} {dtype}" for col, dtype in schema.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
        self.cursor.execute(query)
        self.conn.commit()

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        """
        Универсальная вставка данных (защищена от SQL-инъекций).
        data: словарь вида {"колонка": значение}
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

        self.cursor.execute(query, list(data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    def select(self, table_name: str, condition: str = "", params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Универсальный выбор данных.
        condition: строка условия, например "WHERE chat_id = ?"
        params: кортеж параметров для условия, например (123,)
        """
        query = f"SELECT * FROM {table_name} {condition};"
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        # Конвертируем sqlite3.Row в стандартные словари Python
        return [dict(row) for row in rows]

    def close(self) -> None:
        """Закрытие соединения с базой данных."""
        if self.conn:
            self.conn.close()