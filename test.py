# test.py
from table_processor import Table, load_csv, save_csv, save_text

print("=== ТЕСТ ЗАПУЩЕН ===")

# 1. СОЗДАЕМ ТАБЛИЦУ
print("1. Создаем таблицу...")
data = [
    [1, "Анна", 25, 50000],
    [2, "Борис", 30, 60000],
    [3, "Виктор", 35, 70000]
]
headers = ["id", "имя", "возраст", "зарплата"]
table = Table(data, headers, index_col="id")

print("Созданная таблица:")
table.print_table()

# 2. СОХРАНЯЕМ В ФАЙЛЫ
print("\n2. Сохраняем в файлы...")
save_csv(table, "сотрудники.csv")
save_text(table, "сотрудники.txt")
print("✓ Файлы сохранены!")

# 3. ЗАГРУЖАЕМ ОБРАТНО
print("\n3. Загружаем из CSV...")
loaded_table = load_csv("сотрудники.csv")

# УСТАНАВЛИВАЕМ ТИПЫ ДАННЫХ
print("Устанавливаем типы данных...")
loaded_table.set_column_types({
    "id": int,
    "возраст": int, 
    "зарплата": int
}, by_number=False)

print("Загруженная таблица:")
loaded_table.print_table()

# 4. АРИФМЕТИЧЕСКИЕ ОПЕРАЦИИ
print("\n4. Арифметические операции...")
print("Прибавляем 5000 к зарплате:")
new_salaries = loaded_table.add(5000, "зарплата")
new_salaries.print_table()

# 5. ОПЕРАЦИИ СРАВНЕНИЯ И ФИЛЬТРАЦИЯ
print("\n5. Фильтрация...")
age_filter = loaded_table.gr(28, "возраст")
print("Фильтр (старше 28):", age_filter)

older_employees = loaded_table.filter_rows(age_filter)
print("Сотрудники старше 28 лет:")
older_employees.print_table()

print("\n=== ТЕСТ УСПЕШНО ЗАВЕРШЕН ===")