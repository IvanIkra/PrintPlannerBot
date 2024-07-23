**Этот файл представляет собой гайд по использованию важных функций из `db_manage.py`**

1. **update_material(conn, material_name, amount, operation)**
    - **Описание**: Обновляет количество материала в базе данных
    - **Использование**: 
      ```python
      update_material(conn, пла, 700, add)
      update_material(conn, пла, 700, subtract)
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `material_name` (str): Имя материала
      - `amount` (int): Количество материала в граммах.
      - `operation` (str): Операция: добавить(add) / вычесть(subtract)
    - **Возвращает**: Обновленное количество материала в граммах.

2. **add_order(conn, name, link, material, material_amount, recommended_date, importance, settings, cost, payment_info,
              done, creation_date)**
    - **Описание**: Создает новый заказ в базе данных.
    - **Использование**: 
      ```python
      add_order(conn, 'order', 'https://github.com/IvanIkra/PrintPlannerBot/blob/ikra', 'pla', 300, '22.07.2024', 3, 'standart', 1200, False,
              False, '22.07.2024')
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `name` (str): Имя заказа.
      - `link` (str): Ссылка на 3д модель (google disk)
      - `material` (str): Материал.
      - `material_amount` (int): Количество материала в граммах.
      - `recommended_date` (str): Дата, к которой нужно выполнить заказ.
      - `importance` (int): Важность заказа (от 1 до 10).
      - `settings` (str): Настройки печати.
      - `cost` (int): Стоимость.
      - `payment_info` (bool): Был ли заказ оплачен.
      - `done` (bool): Выполнен ли заказ.
      - `creation_date` (str): Дата создания заказа.
    - **Возвращает**: ID заказа, который система выдает автоматически.

3. **delete_unpaid_orders(conn)**
    - **Описание**: Удаляет заказы, которые не были оплачены в течение 10 дней после создания.
    - **Использование**: 
      ```python
      delete_unpaid_orders(conn)
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.


4. **get_order_by_id(conn, order_id)**
    - **Описание**: Выводит всю информацию о заказе по ID.
    - **Использование**: 
      ```python
      get_order_by_id(conn, 21)
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `order_id` (int): ID заказа.
    - **Возвращает**: Все данные заказа.
      

5. **delete_order(conn, order_id)**
    - **Описание**: Удаляет заказ с заданным ID.
    - **Использование**: 
      ```python
      delete_order(conn, 21)
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `order_id` (int): ID заказа.

6. **add_expense(conn, category, amount, date_spent, description)**
    - **Описание**: Вставляет запись о расходе в таблицу расходов.
    - **Использование**: 
      ```python
      add_expense(conn, 'Food', 50.0, '2023-07-01', 'Groceries')
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `category` (str): Категория расхода.
      - `amount` (float): Сумма расхода.
      - `date_spent` (str): Дата, когда был совершен расход.
      - `description` (str): Описание расхода.

7. **add_revenue(conn, order_id, amount, date_received)**
    - **Описание**: Вставляет запись о доходе в таблицу доходов.
    - **Использование**: 
      ```python
      add_revenue(conn, 1, 100.0, '2023-07-01')
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `order_id` (int): ID заказа.
      - `amount` (float): Сумма дохода.
      - `date_received` (str): Дата получения дохода.

8. **get_all_materials_exel(conn, excel_path)**
    - **Описание**: Создает таблицу Exel с наличием материалов по заданному адресу.
    - **Использование**: 
      ```python
      get_all_materials_exel(conn, 'data.xlsx')
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `excel_path` (str): Адрес, по которому будет создан файл.
    - **Возвращает**: Список записей о расходах для указанной категории.

9. **export_last_month_data_to_excel(conn, excel_path)**
    - **Описание**: Экспортирует данные расходов и доходов за последний календарный месяц в файл Excel.
    - **Использование**: 
      ```python
      export_last_month_data_to_excel(conn, 'last_month_data.xlsx')
      ```
    - **Параметры**: 
      - `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
      - `excel_path` (str): Адрес, по которому будет создан файл.

10. **export_orders_to_excel(conn, excel_path, done=True)**

* **Описание**: Экспортирует данные заказов (готовые или неготовые) в файл Excel.
* **Использование**:
  ```python
  export_orders_to_excel(conn, 'orders.xlsx', done=True)
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `excel_path` (str): Адрес, по которому будет создан файл.
  * `done` (bool, опционально): Флаг, указывающий, нужно ли экспортировать готовые заказы (`True`) или неготовые (`False`). По умолчанию `True`.