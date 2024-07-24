Инструкции для каждой функции класса `DatabaseManager`:

### `__init__(self, db_file)`
#### Описание:
Конструктор класса `DatabaseManager`. Инициализирует соединение с базой данных и создаёт все необходимые таблицы.
#### Использование:
```python
db_manager = DatabaseManager('example.db')
```
#### Параметры:
- `db_file`: Имя файла базы данных SQLite.

### `create_connection(self, db_file)`
#### Описание:
Создаёт соединение с базой данных SQLite, указанной в `db_file`.
#### Использование:
Вызывается автоматически при инициализации объекта.

### `create_tables(self)`
#### Описание:
Создаёт все необходимые таблицы в базе данных.
#### Использование:
Вызывается автоматически при инициализации объекта.

### `update_material(self, material_name, amount, operation)`
#### Описание:
Обновляет количество материала в базе данных.
#### Использование:
```python
db_manager.update_material('Steel', 50, 'add')
```
#### Параметры:
- `material_name`: Название материала.
- `amount`: Количество для обновления.
- `operation`: Операция (`'add'` или `'subtract'`).
#### Возвращает:
- Новое количество материала в случае успеха, `-1` если недостаточно материала для вычитания, `0` в случае ошибки.

### `add_order(self, name, link, material, material_amount, recommended_date, importance, settings, cost, payment_info, done, creation_date)`
#### Описание:
Добавляет новый заказ в базу данных.
#### Использование:
```python
db_manager.add_order('Order1', 'http://link.com', 'Steel', 10, '2024-12-01', 1, 'Settings', 100.0, True, False, '2024-07-01')
```
#### Параметры:
- `name`: Имя заказа.
- `link`: Ссылка на заказ.
- `material`: Материал заказа.
- `material_amount`: Количество материала.
- `recommended_date`: Рекомендованная дата.
- `importance`: Важность заказа.
- `settings`: Настройки заказа.
- `cost`: Стоимость заказа.
- `payment_info`: Информация об оплате.
- `done`: Статус выполнения заказа.
- `creation_date`: Дата создания заказа.
#### Возвращает:
- ID добавленного заказа в случае успеха, `-1` в случае ошибки.

### `delete_unpaid_orders(self)`
#### Описание:
Удаляет заказы, которые не были оплачены в течение 10 дней после создания.
#### Использование:
```python
db_manager.delete_unpaid_orders()
```
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `get_order_by_id(self, order_id)`
#### Описание:
Получает информацию о заказе по ID.
#### Использование:
```python
order = db_manager.get_order_by_id(1)
```
#### Параметры:
- `order_id`: ID заказа.
#### Возвращает:
- Запись заказа в случае успеха, `0` в случае ошибки.

### `delete_order(self, order_id)`
#### Описание:
Удаляет заказ по ID.
#### Использование:
```python
db_manager.delete_order(1)
```
#### Параметры:
- `order_id`: ID заказа.
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `add_revenue(self, order_id, amount, date_received)`
#### Описание:
Добавляет запись о доходе от заказа.
#### Использование:
```python
db_manager.add_revenue(1, 100.0, '2024-07-01')
```
#### Параметры:
- `order_id`: ID заказа.
- `amount`: Сумма дохода.
- `date_received`: Дата получения дохода.
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `add_expense(self, category, amount, date_spent, description)`
#### Описание:
Добавляет запись о расходах.
#### Использование:
```python
db_manager.add_expense('Office Supplies', 50.0, '2024-07-01', 'Bought pens and paper')
```
#### Параметры:
- `category`: Категория расходов.
- `amount`: Сумма расходов.
- `date_spent`: Дата расходов.
- `description`: Описание расходов.
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `get_all_materials_excel(self, excel_path)`
#### Описание:
Экспортирует данные из таблицы `inventory` в файл Excel.
#### Использование:
```python
db_manager.get_all_materials_excel('materials.xlsx')
```
#### Параметры:
- `excel_path`: Путь к файлу Excel.
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `get_last_month_date_range(self)`
#### Описание:
Получает начало и конец последнего календарного месяца.
#### Использование:
```python
start_date, end_date = db_manager.get_last_month_date_range()
```
#### Возвращает:
- Кортеж с началом и концом последнего календарного месяца.

### `export_last_month_data_to_excel(self, excel_path)`
#### Описание:
Экспортирует данные расходов и доходов за последний календарный месяц в один файл Excel.
#### Использование:
```python
db_manager.export_last_month_data_to_excel('last_month_data.xlsx')
```
#### Параметры:
- `excel_path`: Путь к файлу Excel.
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `export_orders_to_excel(self, excel_path, done=True)`
#### Описание:
Экспортирует данные заказов в файл Excel.
#### Использование:
```python
db_manager.export_orders_to_excel('orders.xlsx', False)
```
#### Параметры:
- `excel_path`: Путь к файлу Excel.
- `done`: Статус выполнения заказа, по умолчанию True (`True` для выполненных, `False` для невыполненных).
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `export_expenses_and_revenue_between_dates_to_excel(self, start_date, end_date, excel_path)`
#### Описание:
Получает расходы и доходы между указанными датами и сохраняет их в Excel.
#### Использование:
```python
db_manager.export_expenses_and_revenue_between_dates_to_excel('2024-06-01', '2024-06-30', 'expenses_revenue.xlsx')
```
#### Параметры:
- `start_date`: Начальная дата.
- `end_date`: Конечная дата.
- `excel_path`: Путь к файлу Excel.
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `auto_delete_expired_records(self, days)`
#### Описание:
Удаляет записи из указанной таблицы, которые старше определенного количества дней.
#### Использование:
```python
db_manager.auto_delete_expired_records(30)
```
#### Параметры:
- `days`: Количество дней для проверки.
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `get_material_by_name(self, material_name)`
#### Описание:
Получает информацию о материале по названию.
#### Использование:
```python
material = db_manager.get_material_by_name('Steel')
```
#### Параметры:
- `material_name`: Название материала.
#### Возвращает:
- Запись материала в случае успеха, `0` в случае ошибки.

### `get_expenses_by_category(self, category, excel_path)`
#### Описание:
Получает список расходов по категории и экспортирует в Excel.
#### Использование:
```python
db_manager.get_expenses_by_category('Office Supplies', 'office_supplies_expenses.xlsx')
```
#### Параметры:
- `category`: Категория расходов.
-

 `excel_path`: Путь к файлу Excel.
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `update_order_status(self, order_id, done)`
#### Описание:
Обновляет статус заказа по ID.
#### Использование:
```python
db_manager.update_order_status(1, True)
```
#### Параметры:
- `order_id`: ID заказа.
- `done`: Статус выполнения заказа (`True` для выполненного, `False` для невыполненного).
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `close_connection(self)`
#### Описание:
Закрывает соединение с базой данных.
#### Использование:
```python
db_manager.close_connection()
```
#### Возвращает:
- `1` в случае успеха.



# !ВАЖНО!
### В рамках данного проекта пи каждом использовании бд, стоит закрывать соединение и в следующий раз открывать его повторно
Пример работы с бд внутри бота
```python
    user_id = message.from_user.id # Получаем id пользователя в тг
    db_manager = DatabaseManager(f'user{user_id}data.db') # Создаем или подключаемся к индивидуальной бд
    
    # То, что мы хотим сделать
    
    db_manager.close_connection() # Закрываем подключение
```