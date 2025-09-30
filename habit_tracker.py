import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at DATE NOT NULL
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS completions (
        habit_id INTEGER,
        date DATE,
        FOREIGN KEY (habit_id) REFERENCES habits(id)
    )''')
    conn.commit()
    conn.close()


# Добавление новой привычки
def add_habit(name):
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habits (name, created_at) VALUES (?, ?)", (name, datetime.now().date().isoformat()))
    conn.commit()
    conn.close()
    print(f"Привычка '{name}' добавлена.")


# Отметка выполнения привычки
def mark_habit_completed(habit_id, date=None):
    if date is None:
        date = datetime.now().date()
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO completions (habit_id, date) VALUES (?, ?)", (habit_id, date.isoformat()))
    conn.commit()
    conn.close()
    print(f"Привычка отмечена как выполненная на {date.isoformat()}.")


# Получение статистики по привычке
def get_habit_stats(habit_id):
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM habits WHERE id = ?", (habit_id,))
    habit_name = cursor.fetchone()
    if not habit_name:
        print("Привычка не найдена.")
        conn.close()
        return
    habit_name = habit_name[0]
    cursor.execute("SELECT date FROM completions WHERE habit_id = ? ORDER BY date", (habit_id,))
    dates = [row[0] for row in cursor.fetchall()]
    streak = 0
    if dates:
        dates = [datetime.strptime(date, "%Y-%m-%d").date() for date in dates]
        current = datetime.now().date()
        while current in dates:
            streak += 1
            current -= timedelta(days=1)
    conn.close()
    print(f"Привычка: {habit_name}, Текущая серия: {streak} дней")


# Визуализация прогресса привычки
def plot_habit_progress(habit_id):
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM habits WHERE id = ?", (habit_id,))
    habit_name = cursor.fetchone()
    if not habit_name:
        print("Привычка не найдена.")
        conn.close()
        return
    habit_name = habit_name[0]

    # Получаем даты выполнения за последние 30 дней
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    cursor.execute("SELECT date FROM completions WHERE habit_id = ? AND date >= ? ORDER BY date",
                   (habit_id, start_date.isoformat()))
    completed_dates = [datetime.strptime(row[0], "%Y-%m-%d").date() for row in cursor.fetchall()]
    conn.close()

    # Создаём списки для графика
    dates = [start_date + timedelta(days=x) for x in range(31)]
    values = [1 if d in completed_dates else 0 for d in dates]

    # Построение графика
    plt.figure(figsize=(10, 4))
    plt.step(dates, values, where='mid', label=habit_name)
    plt.title(f"Прогресс привычки: {habit_name}")
    plt.xlabel("Дата")
    plt.ylabel("Выполнено (1) / Не выполнено (0)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# Показать все привычки
def list_habits():
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM habits")
    habits = cursor.fetchall()
    conn.close()
    if not habits:
        print("Нет привычек.")
    for habit_id, name in habits:
        print(f"ID: {habit_id}, Привычка: {name}")


# Основной цикл программы
def main():
    init_db()
    try:
        while True:
            print(
                "\n1. Добавить привычку\n2. Отметить выполнение\n3. Показать статистику\n4. Список привычек\n5. Визуализация прогресса\n6. Выход")
            choice = input("Выберите действие (1-6): ").strip()
            if choice == "1":
                name = input("Введите название привычки: ").strip()
                add_habit(name)
            elif choice == "2":
                list_habits()
                habit_id = input("Введите ID привычки: ").strip()
                try:
                    mark_habit_completed(int(habit_id))
                except ValueError:
                    print("Введите корректный ID.")
            elif choice == "3":
                list_habits()
                habit_id = input("Введите ID привычки для статистики: ").strip()
                try:
                    get_habit_stats(int(habit_id))
                except ValueError:
                    print("Введите корректный ID.")
            elif choice == "4":
                list_habits()
            elif choice == "5":
                list_habits()
                habit_id = input("Введите ID привычки для визуализации: ").strip()
                try:
                    plot_habit_progress(int(habit_id))
                except ValueError:
                    print("Введите корректный ID.")
            elif choice == "6":
                print("Программа завершена.")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")
    except KeyboardInterrupt:
        print("\nПрограмма завершена (Ctrl+C).")


if __name__ == "__main__":
    main()