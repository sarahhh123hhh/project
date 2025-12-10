# models/db.py
import sqlite3
from pathlib import Path

DB_NAME = "shelter.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'client')) NOT NULL
        )
    ''')

    # Таблица животных
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS animals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            breed TEXT,
            age INTEGER NOT NULL,
            health_status TEXT,
            description TEXT,
            status TEXT DEFAULT 'available'
        )
    ''')

    # Таблица заявок на усыновление
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS adoption_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id INTEGER,
            client_id INTEGER,
            request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (animal_id) REFERENCES animals (id),
            FOREIGN KEY (client_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("База shelter.db создана/проверена")