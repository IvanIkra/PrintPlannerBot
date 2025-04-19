Инструкции для каждой функции класса `DatabaseManager`:

### `__init__(self, db_file)`
#### Описание:
Конструктор класса `DatabaseManager`. Инициализирует соединение с базой данных и создаёт все необходимые таблицы.
#### Использование:
```python
db_manager = DatabaseManager('example.db')
```
#### Параметры:
- `db_file: str`: Имя файла базы данных SQLite.

### `create_connection(self, db_file)`
#### Описание:
Создаёт соединение с базой данных SQLite, указанной в `db_file`.
#### Использование:
Вызывается автоматически при инициализации объекта.
#### Возвращает:
- `Connection` объект в случае успеха, `None` в случае ошибки.

### `create_tables(self)`
#### Описание:
Создаёт все необходимые таблицы в базе данных.
#### Использование:
Вызывается автоматически при инициализации объекта.
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `update_material(self, material_name, amount, operation)`
#### Описание:
Обновляет количество материала в базе данных.
#### Использование:
```python
db_manager.update_material('Steel', 50, 'add')
```
#### Параметры:
- `material_name: str`: Название материала.
- `amount: int`: Количество для обновления.
- `operation: str`: Операция (`'add'` или `'subtract'`).
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
- `name: str`: Имя заказа.
- `link: str`: Ссылка на заказ.
- `material: str`: Материал заказа.
- `material_amount: int`: Количество материала.
- `recommended_date: str`: Рекомендованная дата.
- `importance: int`: Важность заказа.
- `settings: str`: Настройки заказа.
- `cost: float`: Стоимость заказа.
- `payment_info: bool`: Информация об оплате.
- `done: bool`: Статус выполнения заказа.
- `creation_date: str`: Дата создания заказа.
#### Возвращает:
- ID добавленного заказа в случае успеха, `-1` в случае ошибки.

### `get_pending_orders(self)`
#### Описание:
Получает список всех невыполненных заказов.
#### Использование:
```python
orders = db_manager.get_pending_orders()
```
#### Возвращает:
- Список заказов в случае успеха, пустой список в случае ошибки.

### `export_pending_orders_to_excel(self, excel_path)`
#### Описание:
Экспортирует невыполненные заказы в Excel файл.
#### Использование:
```python
success = db_manager.export_pending_orders_to_excel('pending_orders.xlsx')
```
#### Параметры:
- `excel_path: str`: Путь к файлу Excel.
#### Возвращает:
- `True` в случае успеха, `False` в случае ошибки или отсутствия заказов.

### `delete_unpaid_orders(self)`
#### Описание:
Удаляет заказы, которые не были оплачены в течение 10 дней после создания.
#### Использование:
```python
db_manager.delete_unpaid_orders()
```
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `get_order(self, info, key = 'id')`
#### Описание:
Получает информацию о заказе по ID или имени.
#### Использование:
```python
order = db_manager.get_order(1)  # по ID
order = db_manager.get_order('Order1', 'name')  # по имени
```
#### Параметры:
- `info: str | int`: ID или имя заказа.
- `key: str`: Ключ поиска ('id' или 'name').
#### Возвращает:
- Кортеж с данными заказа в случае успеха, `0` в случае ошибки.

### `delete_order(self, order_id)`
#### Описание:
Удаляет заказ по ID.
#### Использование:
```python
db_manager.delete_order(1)
```
#### Параметры:
- `order_id: int`: ID заказа.
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
- `order_id: int`: ID заказа.
- `amount: float`: Сумма дохода.
- `date_received: str`: Дата получения дохода.
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `add_expense(self, category, amount, date_spent, description)`
#### Описание:
Добавляет запись о расходах.
#### Использование:
```python
db_manager.add_expense('Office Supplies', 50.0, '2024-07-01', 'Bought pens')
```
#### Параметры:
- `category: str`: Категория расходов.
- `amount: float`: Сумма расходов.
- `date_spent: str`: Дата расходов.
- `description: str`: Описание расходов.
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `auto_delete_expired_records(self, days)`
#### Описание:
Удаляет записи заказов, которые старше указанного количества дней.
#### Использование:
```python
db_manager.auto_delete_expired_records(30)
```
#### Параметры:
- `days: int`: Количество дней.
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
- `material_name: str`: Название материала.
#### Возвращает:
- Кортеж (name, quantity) в случае успеха, `0` в случае ошибки.

### `update_order_status(self, order_id, done)`
#### Описание:
Обновляет статус заказа.
#### Использование:
```python
db_manager.update_order_status(1, True)
```
#### Параметры:
- `order_id: int`: ID заказа.
- `done: bool`: Новый статус.
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

### `get_all_materials(self)`
#### Описание:
Получает список всех материалов.
#### Использование:
```python
materials = db_manager.get_all_materials()
```
#### Возвращает:
- Список кортежей (name, quantity) в случае успеха, `0` в случае ошибки.

### `update_order_cost(self, order_id, cost)`
#### Описание:
Обновляет стоимость заказа.
#### Использование:
```python
db_manager.update_order_cost(1, 150.0)
```
#### Параметры:
- `order_id: int`: ID заказа.
- `cost: float`: Новая стоимость.
#### Возвращает:
- `True` в случае успеха, `False` в случае ошибки.

### `close_connection(self)`
#### Описание:
Закрывает соединение с базой данных.
#### Использование:
```python
db_manager.close_connection()
```
#### Возвращает:
- `1` в случае успеха, `0` в случае ошибки.

# !ВАЖНО!
### В рамках данного проекта при каждом использовании БД следует закрывать соединение и в следующий раз открывать его повторно
Пример работы с БД внутри бота:
```python
    user_id = message.from_user.id # Получаем id пользователя в тг
    db_manager = DatabaseManager(f'data/db/user{user_id}data.db') # Создаем или подключаемся к индивидуальной бд
    
    # То, что мы хотим сделать
    
    db_manager.close_connection() # Закрываем подключение
```
```