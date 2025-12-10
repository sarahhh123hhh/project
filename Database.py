import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_name='animal_shelter.db'):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Таблица клиентов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS client (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    login TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    phone TEXT
                )
            ''')

            # Таблица администраторов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    login TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')

            # Таблица животных
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS animal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    species TEXT NOT NULL,
                    breed TEXT,
                    age INTEGER,
                    gender TEXT,
                    description TEXT,
                    photo_url TEXT,
                    health_status TEXT DEFAULT 'здоров',
                    is_available BOOLEAN DEFAULT 1,
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'доступен'
                )
            ''')

            # Таблица заявок на усыновление
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS adoption_request (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    animal_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    comment TEXT,
                    FOREIGN KEY (client_id) REFERENCES client (id),
                    FOREIGN KEY (animal_id) REFERENCES animal (id)
                )
            ''')

            # Создаем индексы для быстрого поиска
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_animal_available ON animal(is_available)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_animal_species ON animal(species)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_request_status ON adoption_request(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_request_client ON adoption_request(client_id)')

            # Создаем тестовых пользователей, если их нет
            self.create_test_data(cursor)

            conn.commit()

    def create_test_data(self, cursor):
        # Проверяем, есть ли уже администраторы
        cursor.execute("SELECT COUNT(*) FROM admin")
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT INTO admin (name, login, password) 
                VALUES (?, ?, ?)
            ''', [
                ('Иван Петров', 'admin', 'admin123'),
                ('Мария Сидорова', 'admin2', 'admin456')
            ])

        # Проверяем, есть ли уже клиенты
        cursor.execute("SELECT COUNT(*) FROM client")
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT INTO client (name, login, password, phone) 
                VALUES (?, ?, ?, ?)
            ''', [
                ('Алексей Смирнов', 'alex', 'pass123', '+79001234567'),
                ('Ольга Иванова', 'olga', 'pass456', '+79007654321'),
                ('Дмитрий Козлов', 'dima', 'pass789', '+79009876543')
            ])

        # Проверяем, есть ли уже животные
        cursor.execute("SELECT COUNT(*) FROM animal")
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT INTO animal (name, species, breed, age, gender, description, health_status, is_available) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                ('Барсик', 'Кот', 'Британский', 2, 'М', 'Ласковый, любит играть', 'здоров', 1),
                ('Шарик', 'Собака', 'Дворняжка', 3, 'М', 'Активный, преданный', 'здоров', 1),
                ('Мурка', 'Кот', 'Сиамская', 1, 'Ж', 'Спокойная, любит спать', 'здоров', 1),
                ('Рекс', 'Собака', 'Овчарка', 4, 'М', 'Охраняет территорию', 'здоров', 1),
                ('Черныш', 'Кот', 'Чёрный', 2, 'М', 'Дружелюбный, любит детей', 'требует ухода', 1),
                ('Ласка', 'Собака', 'Такса', 5, 'Ж', 'Энергичная, любит гулять', 'здоров', 1),
                ('Снежок', 'Кролик', 'Карликовый', 1, 'М', 'Белый пушистый кролик', 'здоров', 1),
                ('Рыжик', 'Кот', 'Персидский', 3, 'М', 'Пушистый, требует ухода', 'здоров', 0)  # уже усыновлен
            ])

        # Проверяем, есть ли уже заявки
        cursor.execute("SELECT COUNT(*) FROM adoption_request")
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT INTO adoption_request (client_id, animal_id, status, comment) 
                VALUES (?, ?, ?, ?)
            ''', [
                (1, 8, 'approved', 'Хочу подарить детям'),
                (2, 1, 'pending', 'Ищу друга для семьи'),
                (3, 2, 'rejected', 'Для охраны дома'),
                (1, 3, 'cancelled', 'Передумал')
            ])