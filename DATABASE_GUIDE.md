**Этот файл представляет собой гайд по использованию функций из `db_manage.py`**

1. **create_connection(db_file)**
    - **Описание**: Создает соединение с базой данных SQLite, указанной в `db_file`.
    - **Использование**: 
      ```python
      conn = create_connection('example.db')
      ```
    - **Параметры**: 
      - `db_file` (str): Имя файла базы данных SQLite.
    - **Возвращает**: Объект соединения с базой данных SQLite.

2. **create_expenses_table(conn)**
    - **Описание**: Создает таблицу для учета расходов в базе данных.
    - **Использование**: 
      ```python
      create_expenses_table(conn)
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.

3. **create_table(conn)**
    - **Описание**: Создает таблицу для инвентаризации материалов в базе данных.
    - **Использование**: 
      ```python
      create_table(conn)
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.

4. **create_revenue_table(conn)**
    - **Описание**: Создает таблицу для учета доходов в базе данных.
    - **Использование**: 
      ```python
      create_revenue_table(conn)
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.

5. **create_orders_table(conn)**
    - **Описание**: Создает или обновляет таблицу заказов в базе данных.
    - **Использование**: 
      ```python
      create_orders_table(conn)
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.

6. **insert_expense(conn, category, amount, date_spent, description)**
    - **Описание**: Вставляет запись о расходе в таблицу расходов.
    - **Использование**: 
      ```python
      insert_expense(conn, 'Food', 50.0, '2023-07-01', 'Groceries')
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `category` (str): Категория расхода.
      - `amount` (float): Сумма расхода.
      - `date_spent` (str): Дата, когда был совершен расход.
      - `description` (str): Описание расхода.

7. **insert_revenue(conn, order_id, amount, date_received)**
    - **Описание**: Вставляет запись о доходе в таблицу доходов.
    - **Использование**: 
      ```python
      insert_revenue(conn, 1, 100.0, '2023-07-01')
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `order_id` (int): ID заказа.
      - `amount` (float): Сумма дохода.
      - `date_received` (str): Дата получения дохода.

8. **get_expenses_by_category(conn, category)**
    - **Описание**: Извлекает расходы из базы данных по заданной категории.
    - **Использование**: 
      ```python
      expenses = get_expenses_by_category(conn, 'Food')
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `category` (str): Категория расходов для извлечения.
    - **Возвращает**: Список записей о расходах для указанной категории.

9. **get_revenue_by_order_id(conn, order_id)**
    - **Описание**: Извлекает доходы из базы данных по заданному ID заказа.
    - **Использование**: 
      ```python
      revenue = get_revenue_by_order_id(conn, 1)
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `order_id` (int): ID заказа.
    - **Возвращает**: Список записей о доходах для указанного ID заказа.

10. **get_last_month_date_range()**
    - **Описание**: Получает даты начала и конца последнего календарного месяца.
    - **Использование**: 
      ```python
      start_date, end_date = get_last_month_date_range()
      ```
    - **Возвращает**: Кортеж, содержащий даты начала и конца последнего календарного месяца.

11. **export_last_month_data_to_excel(conn, excel_path)**
    - **Описание**: Экспортирует данные расходов и доходов за последний календарный месяц в файл Excel.
    - **Использование**: 
      ```python
      export_last_month_data_to_excel(conn, 'last_month_data.xlsx')
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `excel_path` (str): Путь к файлу Excel, в который будут экспортированы данные.
