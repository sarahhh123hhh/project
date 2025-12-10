# export_table.py
import sqlite3
import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
import yaml
import os
import sys

DB_NAME = 'animal_shelter.db'
OUT_DIR = 'out'


def prettify_xml(elem):
    """Форматирует XML-дерево в читаемый вид"""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def get_table_names(cursor):
    """Получает список всех таблиц в базе данных"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]


def get_table_schema(cursor, table_name):
    """Получает схему таблицы"""
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    return cursor.fetchall()


def get_foreign_keys(cursor, table_name):
    """Получает информацию о внешних ключах таблицы"""
    cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
    fks = {}
    for row in cursor.fetchall():
        child_col = row[3]  # from
        parent_table = row[2]  # table
        parent_col = row[4]  # to
        fks[child_col] = (parent_table, parent_col)
    return fks


def fetch_table_data(cursor, table_name):
    """Получает все данные из таблицы"""
    cursor.execute(f'SELECT * FROM "{table_name}"')
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    # Преобразуем в список словарей
    data = []
    for row in rows:
        data.append(dict(zip(columns, row)))

    return data, columns


def export_to_json(data, table_name):
    """Экспорт в JSON формат"""
    filename = f"{OUT_DIR}/{table_name.lower()}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"✓ Экспортировано в JSON: {filename}")
    return filename


def export_to_csv(data, columns, table_name):
    """Экспорт в CSV формат"""
    filename = f"{OUT_DIR}/{table_name.lower()}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in data:
            writer.writerow([row.get(col, '') for col in columns])
    print(f"✓ Экспортировано в CSV: {filename}")
    return filename


def export_to_xml(data, table_name):
    """Экспорт в XML формат"""
    root = ET.Element(table_name.lower())

    for record in data:
        item = ET.SubElement(root, "record")
        for key, value in record.items():
            child = ET.SubElement(item, key.replace(' ', '_').lower())
            child.text = str(value) if value is not None else ""

    filename = f"{OUT_DIR}/{table_name.lower()}.xml"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(prettify_xml(root))
    print(f"✓ Экспортировано в XML: {filename}")
    return filename


def export_to_yaml(data, table_name):
    """Экспорт в YAML формат"""
    filename = f"{OUT_DIR}/{table_name.lower()}.yaml"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, indent=2)
        print(f"✓ Экспортировано в YAML: {filename}")
        return filename
    except ImportError:
        print("⚠️  Библиотека PyYAML не установлена. Пропускаем экспорт в YAML.")
        return None


def export_table(table_name):
    """Экспортирует указанную таблицу во все форматы"""
    os.makedirs(OUT_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"\n{'=' * 60}")
    print(f"ЭКСПОРТ ТАБЛИЦЫ: {table_name}")
    print(f"{'=' * 60}")

    # Проверяем существование таблицы
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if not cursor.fetchone():
        print(f"❌ Таблица '{table_name}' не найдена!")
        conn.close()
        return

    # Получаем данные
    data, columns = fetch_table_data(cursor, table_name)

    if not data:
        print(f"⚠️  Таблица '{table_name}' пуста!")
    else:
        print(f"Найдено записей: {len(data)}")

        # Экспортируем во все форматы
        files = []
        files.append(export_to_json(data, table_name))
        files.append(export_to_csv(data, columns, table_name))
        files.append(export_to_xml(data, table_name))
        yaml_file = export_to_yaml(data, table_name)
        if yaml_file:
            files.append(yaml_file)

    conn.close()

    # Выводим статистику
    if data:
        print(f"\n{'=' * 60}")
        print("РЕЗУЛЬТАТЫ ЭКСПОРТА:")
        print(f"{'=' * 60}")

        for file_path in files:
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                file_name = os.path.basename(file_path)
                print(f"• {file_name} ({file_size} байт)")

        print(f"\n📁 Все файлы сохранены в папке: {os.path.abspath(OUT_DIR)}")
    print(f"{'=' * 60}")


def show_table_info(cursor, table_name):
    """Показывает информацию о таблице"""
    # Схема таблицы
    schema = get_table_schema(cursor, table_name)
    print(f"\nСхема таблицы '{table_name}':")
    for col in schema:
        print(f"  {col[1]} ({col[2]})" + (" PRIMARY KEY" if col[5] else ""))

    # Внешние ключи
    fks = get_foreign_keys(cursor, table_name)
    if fks:
        print("\nВнешние ключи:")
        for child_col, (parent_table, parent_col) in fks.items():
            print(f"  {child_col} → {parent_table}.{parent_col}")

    # Количество записей
    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    count = cursor.fetchone()[0]
    print(f"\nКоличество записей: {count}")

    # Первые 3 записи
    if count > 0:
        cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 3')
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        print("\nПервые 3 записи:")
        for row in rows:
            print("  ", dict(zip(columns, row)))


def interactive_mode():
    """Интерактивный режим работы"""
    if not os.path.exists(DB_NAME):
        print(f"❌ Файл базы данных '{DB_NAME}' не найден!")
        print("   Сначала запустите main.py для создания базы данных")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    tables = get_table_names(cursor)

    if not tables:
        print("❌ В базе данных нет таблиц!")
        conn.close()
        return

    print(f"\n{'=' * 60}")
    print("ДОСТУПНЫЕ ТАБЛИЦЫ В БАЗЕ ДАННЫХ:")
    print(f"{'=' * 60}")

    for i, table in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM '{table}'")
        count = cursor.fetchone()[0]
        print(f"{i}. {table} ({count} записей)")

    print(f"{'=' * 60}")

    while True:
        try:
            choice = input("\nВыберите таблицу (номер или название, 0 для выхода): ").strip()

            if choice == '0':
                print("Выход из программы.")
                break

            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(tables):
                    table_name = tables[choice_num - 1]
                else:
                    print("❌ Неверный номер!")
                    continue
            else:
                if choice in tables:
                    table_name = choice
                else:
                    print(f"❌ Таблица '{choice}' не найдена!")
                    continue

            # Показываем информацию о таблице
            show_table_info(cursor, table_name)

            confirm = input(f"\nЭкспортировать таблицу '{table_name}'? (да/нет): ").strip().lower()
            if confirm in ['да', 'д', 'y', 'yes']:
                conn.close()
                export_table(table_name)
                break
            else:
                print("Экспорт отменен.")
                continue

        except ValueError:
            print("❌ Неверный ввод!")
        except sqlite3.Error as e:
            print(f"❌ Ошибка базы данных: {e}")
            break

    conn.close()


def main():
    """Основная функция программы"""
    print(f"\n{'=' * 60}")
    print("СИСТЕМА ЭКСПОРТА ДАННЫХ ПРИЮТА ЖИВОТНЫХ")
    print("Экспорт таблиц в форматы JSON, CSV, XML, YAML")
    print(f"{'=' * 60}")

    # Проверяем существование базы данных
    if not os.path.exists(DB_NAME):
        print(f"❌ Файл базы данных '{DB_NAME}' не найден!")
        print("   Сначала запустите main.py для создания базы данных")
        return

    # Обработка аргументов командной строки
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        export_table(table_name)
    else:
        # Интерактивный режим
        interactive_mode()


if __name__ == "__main__":
    main()