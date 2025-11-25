# main.py
from models.crud_operations import AnimalCRUD, AdoptionCRUD, UserCRUD
from models.models import Animal, AdoptionRequest


class AnimalShelterApp:
    def __init__(self):
        self.animal_crud = AnimalCRUD()
        self.adoption_crud = AdoptionCRUD()
        self.user_crud = UserCRUD()
        self.current_user = None

    def display_main_menu(self):
        print("\n" + "="*50)
        print("   СИСТЕМА УЧЕТА ЖИВОТНЫХ В ПРИЮТЕ")
        print("="*50)
        print("1. Администратор")
        print("2. Клиент")
        print("0. Выход")
        print("="*50)

    def display_admin_menu(self):
        print("\n" + "-"*40)
        print("АДМИНИСТРАТОР")
        print("-"*40)
        print("1. Все животные (включая усыновлённых)")
        print("2. Добавить животное")
        print("3. Удалить/изменить статус животного")
        print("4. Все заявки на усыновление")
        print("5. Одобрить заявку")
        print("6. Отклонить заявку")
        print("0. Назад")

    def display_client_menu(self):
        print("\n" + "-"*40)
        print("КЛИЕНТ")
        print("-"*40)
        print("1. Посмотреть доступных животных")
        print("2. Подать заявку на усыновление")
        print("3. Мои заявки")
        print("4. Отменить заявку")
        print("0. Назад")

    def run(self):
        while True:
            self.display_main_menu()
            choice = input("Выберите роль (0-2): ").strip()

            if choice == '0':
                print("До свидания!")
                break

            role = 'admin' if choice == '1' else 'client' if choice == '2' else None
            if not role:
                print("Неверный выбор!")
                continue

            # Авторизация
            username = input("Логин: ").strip()
            password = input("Пароль: ").strip()
            user = self.user_crud.authenticate(username, password, role)
            if not user:
                print("Неверный логин, пароль или роль!")
                continue

            self.current_user = user
            print(f"Добро пожаловать, {user['name']}!")

            if role == 'admin':
                self.admin_panel()
            else:
                self.client_panel()

    def admin_panel(self):
        while True:
            self.display_admin_menu()
            ch = input("Действие: ").strip()
            if ch == '1': self.show_all_animals()
            elif ch == '2': self.add_animal()
            elif ch == '3': self.remove_animal()
            elif ch == '4': self.show_all_requests()
            elif ch == '5': self.approve_request()
            elif ch == '6': self.reject_request()
            elif ch == '0':
                self.current_user = None
                break

    def client_panel(self):
        while True:
            self.display_client_menu()
            ch = input("Действие: ").strip()
            if ch == '1': self.show_available_animals()
            elif ch == '2': self.submit_request()
            elif ch == '3': self.show_my_requests()
            elif ch == '4': self.cancel_request()
            elif ch == '0':
                self.current_user = None
                break

    # === Функции ===
    def show_all_animals(self):
        print("\nВсе животные:")
        animals = self.animal_crud.get_all_animals()
        if not animals:
            print("Нет животных.")
            return
        for a in animals:
            print(f"ID: {a[0]} | {a[1]} ({a[2]}) | {a[3]} | {a[4]} лет | Статус: {a[7]}")

    def show_available_animals(self):
        print("\nДоступны для усыновления:")
        animals = self.animal_crud.get_available_animals()
        if not animals:
            print("Нет доступных животных.")
            return
        for a in animals:
            print(f"ID: {a[0]} | {a[1]} | {a[2]} | Порода: {a[3]} | Возраст: {a[4]} | Здоровье: {a[6]}")

    def add_animal(self):
        name = input("Кличка: ")
        species = input("Вид: ")
        breed = input("Порода: ")
        age = int(input("Возраст: "))
        health = input("Здоровье: ")
        animal = Animal(name=name, species=species, breed=breed, age=age, health_status=health)
        id_ = self.animal_crud.add_animal(animal)
        print(f"Добавлено! ID: {id_}")

    def remove_animal(self):
        id_ = int(input("ID животного: "))
        reason = input("Причина (усыновлено/умерло и т.д.): ")
        new_status = f"усыновлено ({reason})" if "усынов" in reason.lower() else reason
        if self.animal_crud.update_status(id_, new_status):
            print("Статус обновлён.")
        else:
            print("Животное не найдено.")

    def show_all_requests(self):
        print("\nВсе заявки:")
        requests = self.adoption_crud.get_all_requests()
        if not requests:
            print("Нет заявок.")
            return
        for r in requests:
            status = {"pending":"На рассмотрении", "approved":"Одобрена", "rejected":"Отклонена", "cancelled":"Отменена"}.get(r[4], r[4])
            print(f"№{r[0]} | Животное: {r[7]} (ID {r[1]}) | Клиент: {r[5]} ({r[6]}) | {status} | Дата: {r[3]}")

    def approve_request(self):
        id_ = int(input("ID заявки для одобрения: "))
        if self.adoption_crud.approve_request(id_):
            print("Заявка одобрена, животное помечено как усыновлённое.")
        else:
            print("Ошибка или заявка не найдена.")

    def reject_request(self):
        id_ = int(input("ID заявки для отклонения: "))
        if self.adoption_crud.reject_request(id_):
            print("Заявка отклонена.")
        else:
            print("Ошибка или заявка не найдена.")

    def submit_request(self):
        self.show_available_animals()
        try:
            id_ = int(input("\nID животного: "))
            req = AdoptionRequest(animal_id=id_, client_id=self.current_user['id'])
            req_id = self.adoption_crud.create_request(req)
            if req_id:
                print(f"Заявка подана! Номер: {req_id}")
            else:
                print("Не удалось подать заявку (возможно, животное недоступно).")
        except ValueError:
            print("Неверный ID.")

    def show_my_requests(self):
        print(f"\nВаши заявки ({self.current_user['name']}):")
        requests = self.adoption_crud.get_requests_by_client_id(self.current_user['id'])
        if not requests:
            print("Нет заявок.")
            return
        for r in requests:
            status = {"pending":"На рассмотрении", "approved":"Одобрена", "rejected":"Отклонена", "cancelled":"Отменена"}.get(r[4], r[4])
            print(f"№{r[0]} | Животное: {r[6]} | Статус: {status} | Дата: {r[3]}")

    def cancel_request(self):
        self.show_my_requests()
        try:
            id_ = int(input("\nНомер заявки для отмены: "))
            if self.adoption_crud.cancel_request(id_, self.current_user['id']):
                print("Заявка отменена.")
            else:
                print("Не удалось отменить (возможно, уже обработана или не ваша).")
        except ValueError:
            print("Неверный ввод.")


if __name__ == "__main__":
    app = AnimalShelterApp()
    app.run()