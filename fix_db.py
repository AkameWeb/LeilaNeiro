"""
Скрипт для исправления структуры базы данных
Добавляет недостающие колонки
"""
import sqlite3
import os


def fix_database():
    db_path = "data/leila.db"

    if not os.path.exists(db_path):
        print("❌ База данных не найдена. Запустите программу сначала.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Добавляем колонку count в long_term_memory
    try:
        cursor.execute("ALTER TABLE long_term_memory ADD COLUMN count INTEGER DEFAULT 1")
        print("✅ Добавлен столбец count в long_term_memory")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️ Столбец count уже существует")
        else:
            print(f"❌ Ошибка: {e}")

    # Добавляем колонку learned_at в learned_words
    try:
        cursor.execute("ALTER TABLE learned_words ADD COLUMN learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        print("✅ Добавлен столбец learned_at в learned_words")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️ Столбец learned_at уже существует")
        else:
            print(f"❌ Ошибка: {e}")

    # Добавляем колонку last_used в long_term_memory
    try:
        cursor.execute("ALTER TABLE long_term_memory ADD COLUMN last_used TIMESTAMP")
        print("✅ Добавлен столбец last_used в long_term_memory")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️ Столбец last_used уже существует")

    # Добавляем колонку source в long_term_memory
    try:
        cursor.execute("ALTER TABLE long_term_memory ADD COLUMN source TEXT DEFAULT 'dialogue'")
        print("✅ Добавлен столбец source в long_term_memory")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️ Столбец source уже существует")

    conn.commit()
    conn.close()

    print("\n✨ База данных успешно обновлена!")


if __name__ == "__main__":
    fix_database()