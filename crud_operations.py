# models/crud_operations.py
import sqlite3
from models.database import Database
from models import Animal, AdoptionRequest
from typing import List, Tuple, Optional, Dict


class AnimalCRUD:
    def __init__(self):
        self.db = Database()

    def add_animal(self, animal: Animal) -> int:
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO Animals (name, species, breed, age, arrival_date, health_status, status)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (animal.name, animal.species, animal.breed, animal.age,
                   animal.arrival_date, animal.health_status, animal.status))
        conn.commit()
        id_ = c.lastrowid
        conn.close()
        return id_

    def get_all_animals(self) -> List[Tuple]:
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM Animals ORDER BY animal_id")
        rows = c.fetchall()
        conn.close()
        return rows

    def get_available_animals(self) -> List[Tuple]:
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM Animals WHERE status = 'в приюте'")
        rows = c.fetchall()
        conn.close()
        return rows

    def update_status(self, animal_id: int, new_status: str) -> bool:
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("UPDATE Animals SET status = ? WHERE animal_id = ?", (new_status, animal_id))
        updated = c.rowcount > 0
        conn.commit()
        conn.close()
        return updated


class AdoptionCRUD:
    def __init__(self):
        self.db = Database()

    def create_request(self, request: AdoptionRequest) -> Optional[int]:
        conn = self.db.get_connection()
        c = conn.cursor()
        # Проверка доступности
        c.execute("SELECT status FROM Animals WHERE animal_id = ?", (request.animal_id,))
        row = c.fetchone()
        if not row or row[0] != 'в приюте':
            conn.close()
            return None
        try:
            c.execute('''INSERT INTO AdoptionRequests (animal_id, client_id, request_date, status)
                         VALUES (?, ?, ?, ?)''',
                      (request.animal_id, request.client_id, request.request_date, request.status))
            conn.commit()
            id_ = c.lastrowid
            conn.close()
            return id_
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def get_all_requests(self) -> List[Tuple]:
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute('''SELECT ar.request_id, ar.animal_id, ar.client_id, ar.request_date, ar.status,
                            u.name, u.phone, a.name
                     FROM AdoptionRequests ar
                     JOIN Users u ON ar.client_id = u.user_id
                     JOIN Animals a ON ar.animal_id = a.animal_id
                     ORDER BY ar.request_date DESC''')
        rows = c.fetchall()
        conn.close()
        return rows

    def get_requests_by_client_id(self, client_id: int) -> List[Tuple]:
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute('''SELECT ar.request_id, ar.animal_id, ar.client_id, ar.request_date, ar.status,
                            a.name
                     FROM AdoptionRequests ar
                     JOIN Animals a ON ar.animal_id = a.animal_id
                     WHERE ar.client_id = ? AND ar.status != 'cancelled'
                     ORDER BY ar.request_date DESC''', (client_id,))
        rows = c.fetchall()
        conn.close()
        return rows

    def approve_request(self, request_id: int) -> bool:
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("UPDATE AdoptionRequests SET status = 'approved' WHERE request_id = ?", (request_id,))
        if c.rowcount == 0:
            conn.close()
            return False
        c.execute("UPDATE Animals SET status = 'усыновлено' WHERE animal_id = (SELECT animal_id FROM AdoptionRequests WHERE request_id = ?)", (request_id,))
        conn.commit()
        conn.close()
        return True

    def reject_request(self, request_id: int) -> bool:
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("UPDATE AdoptionRequests SET status = 'rejected' WHERE request_id = ?", (request_id,))
        success = c.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def cancel_request(self, request_id: int, client_id: int) -> bool:
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("UPDATE AdoptionRequests SET status = 'cancelled' WHERE request_id = ? AND client_id = ? AND status = 'pending'",
                  (request_id, client_id))
        success = c.rowcount > 0
        conn.commit()
        conn.close()
        return success


class UserCRUD:
    def __init__(self):
        self.db = Database()

    def authenticate(self, username: str, password: str, role: str) -> Optional[Dict]:
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT user_id, username, password, role, name, phone FROM Users WHERE username = ? AND password = ? AND role = ?",
                  (username, password, role))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'role': row[3],
                'name': row[4],
                'phone': row[5]
            }
        return None