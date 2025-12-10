# models/database.py
import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_name='animal_shelter.db'):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        conn = self.get_connection()
        c = conn.cursor()

        # Таблица животных
        c.execute('''CREATE TABLE IF NOT EXISTS Animals (
                        animal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL, species TEXT NOT NULL, breed TEXT,
                        age INTEGER, arrival_date TEXT, health_status TEXT, status TEXT DEFAULT 'в приюте')''')

        # Таблица пользователей (админы и клиенты)
        c.execute('''CREATE TABLE IF NOT EXISTS Users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL,  -- 'admin' or 'client'
                        name TEXT NOT NULL,
                        phone TEXT NOT NULL)''')

        # Таблица заявок (теперь с client_id)
        c.execute('''CREATE TABLE IF NOT EXISTS AdoptionRequests (
                        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        animal_id INTEGER NOT NULL,
                        client_id INTEGER NOT NULL,
                        request_date TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        FOREIGN KEY (animal_id) REFERENCES Animals (animal_id),
                        FOREIGN KEY (client_id) REFERENCES Users (user_id))''')

        # Тестовые данные: животные
        c.execute("SELECT COUNT(*) FROM Animals")
        if c.fetchone()[0] == 0:
            c.executemany('''INSERT INTO Animals (name, species, breed, age, arrival_date, health_status, status)
                             VALUES (?, ?, ?, ?, ?, ?, ?)''', [
                ('Барсик', 'Кот', 'Дворовый', 3, '2025-01-10', 'Здоров', 'в приюте'),
                ('Мурка', 'Кот', 'Сиамская', 2, '2025-02-01', 'Здорова', 'в приюте'),
                ('Шарик', 'Собака', 'Овчарка', 4, '2025-01-20', 'Здоров', 'в приюте'),
            ])

        # Тестовые данные: пользователи
        c.execute("SELECT COUNT(*) FROM Users")
        if c.fetchone()[0] == 0:
            users = [
                ('admin1', 'pass1', 'admin', 'Admin One', '+123456789'),
                ('admin2', 'pass2', 'admin', 'Admin Two', '+987654321'),
                ('client1', 'pass1', 'client', 'Client One', '+111222333'),
                ('client2', 'pass2', 'client', 'Client Two', '+444555666'),
            ]
            c.executemany('''INSERT INTO Users (username, password, role, name, phone)
                             VALUES (?, ?, ?, ?, ?)''', users)

        conn.commit()
        conn.close()