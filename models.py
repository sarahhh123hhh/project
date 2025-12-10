# models/models.py
from datetime import datetime
from typing import Optional


class Animal:
    """Модель животного"""
    def __init__(
        self,
        name: str,
        species: str,
        breed: Optional[str] = None,
        age: Optional[int] = None,
        health_status: Optional[str] = None,
        arrival_date: Optional[str] = None,
        status: str = "в приюте"
    ):
        self.name = name.strip()
        self.species = species.strip()
        self.breed = (breed or "").strip()
        self.age = age
        self.health_status = (health_status or "").strip()
        self.arrival_date = arrival_date or datetime.now().strftime("%Y-%m-%d")
        self.status = status


class AdoptionRequest:
    """Модель заявки на усыновление"""
    def __init__(
        self,
        animal_id: int,
        client_id: int,
        status: str = "pending",
        request_date: Optional[str] = None
    ):
        self.animal_id = animal_id
        self.client_id = client_id
        self.status = status
        self.request_date = request_date or datetime.now().strftime("%Y-%m-%d %H:%M")


class User:
    """Модель пользователя (админ/клиент)"""
    def __init__(
        self,
        username: str,
        password: str,
        role: str,
        name: str,
        phone: str,
        user_id: Optional[int] = None
    ):
        self.user_id = user_id
        self.username = username.strip()
        self.password = password  # plain text
        self.role = role
        self.name = name.strip()
        self.phone = phone.strip()