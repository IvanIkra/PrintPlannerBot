### Руководство по функциям

#### `create_connection(db_file)`
* **Описание**: Создать соединение с базой данных SQLite, указанной в `db_file`.
* **Использование**:
  ```python
  conn = create_connection('database.db')
  ```
* **Параметры**:
  * `db_file` (str): Путь к файлу базы данных SQLite.

#### `create_expenses_table(conn)`
* **Описание**: Создать таблицу для учёта расходов в базе данных.
* **Использование**:
  ```python
  create_expenses_table(conn)
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.

#### `create_table(conn)`
* **Описание**: Создать таблицу в базе данных для материалов.
* **Использование**:
  ```python
  create_table(conn)
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.

#### `create_revenue_table(conn)`
* **Описание**: Создать таблицу для учёта доходов в базе данных.
* **Использование**:
  ```python
  create_revenue_table(conn)
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.

#### `create_orders_table(conn)`
* **Описание**: Создать или обновить таблицу заказов в базе данных.
* **Использование**:
  ```python
  create_orders_table(conn)
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.

#### `update_material(conn, material_name, amount, operation)`
* **Описание**: Обновить количество материала в базе данных.
* **Использование**:
  ```python
  update_material(conn, 'Material1', 10, 'add')
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `material_name` (str): Название материала.
  * `amount` (int): Количество для добавления или вычитания.
  * `operation` (str): Операция ('add' или 'subtract').

#### `add_order(conn, name, link, material, material_amount, recommended_date, importance, settings, cost, payment_info, done, creation_date)`
* **Описание**: Добавить новый заказ в базу данных.
* **Использование**:
  ```python
  add_order(conn, 'Order1', 'http://example.com', 'Material1', 10, '2024-07-20', 1, 'Settings1', 100.0, True, True, '2024-07-01')
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `name` (str): Название заказа.
  * `link` (str): Ссылка на заказ.
  * `material` (str): Материал заказа.
  * `material_amount` (int): Количество материала.
  * `recommended_date` (str): Рекомендованная дата выполнения.
  * `importance` (int): Важность заказа.
  * `settings` (str): Настройки заказа.
  * `cost` (float): Стоимость заказа.
  * `payment_info` (bool): Информация об оплате.
  * `done` (bool): Статус выполнения заказа.
  * `creation_date` (str): Дата создания заказа.

#### `delete_unpaid_orders(conn)`
* **Описание**: Удалить заказы, которые не были оплачены в течение 10 дней после создания.
* **Использование**:
  ```python
  delete_unpaid_orders(conn)
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.

#### `get_order_by_id(conn, order_id)`
* **Описание**: Получить информацию о заказе по ID.
* **Использование**:
  ```python
  get_order_by_id(conn, 1)
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `order_id` (int): ID заказа.

#### `delete_order(conn, order_id)`
* **Описание**: Удалить заказ по ID.
* **Использование**:
  ```python
  delete_order(conn, 1)
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `order_id` (int): ID заказа.

#### `add_revenue(conn, order_id, amount, date_received)`
* **Описание**: Добавить запись о доходе от заказа.
* **Использование**:
  ```python
  add_revenue(conn, 1, 500.0, '2024-07-01')
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `order_id` (int): ID заказа.
  * `amount` (float): Сумма дохода.
  * `date_received` (str): Дата получения дохода.

#### `add_expense(conn, category, amount, date_spent, description)`
* **Описание**: Добавить запись о расходах.
* **Использование**:
  ```python
  add_expense(conn, 'Food', 50.0, '2024-07-01', 'Groceries')
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `category` (str): Категория расхода.
  * `amount` (float): Сумма расхода.
  * `date_spent` (str): Дата расхода.
  * `description` (str): Описание расхода.

#### `get_all_materials_exel(conn, excel_path)`
* **Описание**: Экспортировать данные из таблицы inventory в файл Excel.
* **Использование**:
  ```python
  get_all_materials_exel(conn, 'materials.xlsx')
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `excel_path` (str): Адрес, по которому будет создан файл.

#### `get_last_month_date_range()`
* **Описание**: Получить начало и конец последнего календарного месяца.
* **Использование**:
  ```python
  start_date, end_date = get_last_month_date_range()
  ```
* **Параметры**: Нет.

#### `export_last_month_data_to_excel(conn, excel_path)`
* **Описание**: Экспортировать данные расходов и доходов за последний календарный месяц в один файл Excel.
* **Использование**:
  ```python
  export_last_month_data_to_excel(conn, 'last_month_data.xlsx')
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `excel_path` (str): Адрес, по которому будет создан файл.

#### `export_orders_to_excel(conn, excel_path, done=True)`
* **Описание**: Экспортировать данные заказов в файл Excel.
* **Использование**:
  ```python
  export_orders_to_excel(conn, 'orders.xlsx', done=True)
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `excel_path` (str): Адрес, по которому будет создан файл.
  * `done` (bool, опционально): Флаг, указывающий, нужно ли экспортировать готовые заказы (True) или неготовые (False). По умолчанию True.

#### `export_expenses_and_revenue_between_dates_to_excel(conn, start_date, end_date, excel_path)`
* **Описание**: Получить расходы и доходы между указанными датами и сохранить их в Excel.
* **Использование**:
  ```python
  export_expenses_and_revenue_between_dates_to_excel(conn, '2024-06-01', '2024-07-01', 'expenses_and_revenue.xlsx')
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `start_date` (str): Начальная дата в формате 'YYYY-MM-DD'.
  * `end_date` (str): Конечная дата в формате 'YYYY-MM-DD'.
  * `excel_path` (str): Адрес, по которому будет создан файл.

#### `auto_delite_expired_records(conn, table, date_column, days)`
* **Описание**: Удалить записи из указанной таблицы, которые старше определенного количества дней.
* **Использование**:
  ```python
  auto_delite_expired_records(conn, 'orders', 'creation_date', 30)
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `table`

 (str): Название таблицы.
  * `date_column` (str): Название столбца с датой.
  * `days` (int): Количество дней, после которых записи считаются устаревшими.

#### `get_material_by_name(conn, material_name)`
* **Описание**: Получить информацию о материале по названию.
* **Использование**:
  ```python
  get_material_by_name(conn, 'Material1')
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `material_name` (str): Название материала.

#### `get_expenses_by_category(conn, category, excel_path)`
* **Описание**: Получить список расходов по категории и экспортировать в Excel.
* **Использование**:
  ```python
  get_expenses_by_category(conn, 'Food', 'expenses_food.xlsx')
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `category` (str): Категория расходов.
  * `excel_path` (str): Адрес, по которому будет создан файл.

#### `update_order_status(conn, order_id, done)`
* **Описание**: Обновить статус заказа по ID.
* **Использование**:
  ```python
  update_order_status(conn, 1, False)
  ```
* **Параметры**:
  * `conn` (sqlite3.Connection): Объект соединения с базой данных SQLite.
  * `order_id` (int): ID заказа.
  * `done` (bool): Новый статус заказа (True для готового, False для неготового).