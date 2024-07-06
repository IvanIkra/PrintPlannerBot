import sqlite3
import datetime


def create_connection(db_file):
    """ Создать соединение с базой данных SQLite, указанной в db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connected to the database successfully")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


def create_expenses_table(conn):
    """ Создать таблицу для учёта расходов в базе данных """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                amount REAL,
                date_spent TEXT,
                description TEXT
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def create_table(conn):
    """ Создать таблицу в базе данных для материалов """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                material_name TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def create_revenue_table(conn):
    """ Создать таблицу для учёта доходов в базе данных """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revenue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                amount REAL,
                date_received TEXT,
                FOREIGN KEY(order_id) REFERENCES orders(id)
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)


# Вы правда это читаете?(IvanIkra) - Да(s1ngul0r)
def create_orders_table(conn):
    """ Создать или обновить таблицу заказов в базе данных """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                link TEXT,
                material TEXT,
                material_amount INTEGER,
                recommended_date TEXT,
                importance INTEGER,
                settings TEXT,
                cost REAL,
                payment_info BOOLEAN,
                done BOOLEAN,
                creation_date TEXT
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def update_material(conn, material_name, amount, operation):
    """ Обновить количество материала в базе данных """
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT quantity FROM inventory WHERE material_name = ?', (material_name,))
        result = cursor.fetchone()

        if operation == 'add':
            if result:
                new_quantity = result[0] + amount
                cursor.execute('UPDATE inventory SET quantity = ? WHERE material_name = ?',
                               (new_quantity, material_name))
            else:
                cursor.execute('INSERT INTO inventory (material_name, quantity) VALUES (?, ?)', (material_name, amount))
        elif operation == 'subtract':
            if result and result[0] >= amount:
                new_quantity = result[0] - amount
                cursor.execute('UPDATE inventory SET quantity = ? WHERE material_name = ?',
                               (new_quantity, material_name))
            else:
                return "Ошибка: недостаточно материала для вычитания."
        conn.commit()
        return f"Обновленное количество {material_name}: {new_quantity if 'new_quantity' in locals() else amount} грамм"
    except sqlite3.Error as e:
        print(e)
        return "Ошибка при обновлении базы данных."


def add_order(conn, name, link, material, material_amount, recommended_date, importance, settings, cost, payment_info,
              done, creation_date):
    """ Добавить новый заказ в базу данных """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (name, link, material, material_amount, recommended_date, importance, settings, cost, payment_info, done, creation_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, link, material, material_amount, recommended_date, importance, settings, cost, payment_info, done,
              creation_date))
        conn.commit()
        return f'Заказ добавлен успешно, его ID: {cursor.lastrowid}'
    except sqlite3.Error as e:
        print(e)


def delete_unpaid_orders(conn):
    """ Удалить заказы, которые не были оплачены в течение 10 дней после создания """
    try:
        cursor = conn.cursor()
        ten_days_ago = datetime.datetime.now() - datetime.timedelta(days=10)
        ten_days_ago_str = ten_days_ago.strftime('%Y-%m-%d')
        cursor.execute('''
            DELETE FROM orders 
            WHERE creation_date <= ? AND (payment_info = 0 OR payment_info IS NULL)
        ''', (ten_days_ago_str,))
        conn.commit()
        print(f"Удалены все неоплаченные заказы, созданные более 10 дней назад и до {ten_days_ago_str}")
    except sqlite3.Error as e:
        print(e)


def get_order_by_id(conn, order_id):
    """ Получить информацию о заказе по ID """
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(e)


def delete_order(conn, order_id):
    """ Удалить заказ по ID """
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def add_revenue(conn, order_id, amount, date_received):
    """ Добавить запись о доходе от заказа """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO revenue (order_id, amount, date_received)
            VALUES (?, ?, ?)
        ''', (order_id, amount, date_received))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def get_all_revenue(conn):
    """ Получить все записи о доходах """
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM revenue')
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(e)


def get_orders_sorted_by(conn, sort_by='recommended_date'):
    """ Получить список всех ID заказов, отсортированных по указанному критерию, включая дату или важность """
    try:
        cursor = conn.cursor()
        if sort_by == 'importance':
            cursor.execute('SELECT id, importance FROM orders ORDER BY importance DESC')
        else:  # По умолчанию сортировка по recommended_date
            cursor.execute('SELECT id, recommended_date FROM orders ORDER BY recommended_date')
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(e)


def add_expense(conn, category, amount, date_spent, description):
    """ Добавить запись о расходах """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (category, amount, date_spent, description)
            VALUES (?, ?, ?, ?)
        ''', (category, amount, date_spent, description))
        conn.commit()
        return 'Запись о расходе добавлена'
    except sqlite3.Error as e:
        print(e)


def get_all_expenses(conn):
    """ Получить все записи о расходах """
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses')
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(e)


def get_financial_summary(conn):
    """ Получить сводку финансов за текущий календарный месяц и за все время """
    try:
        cursor = conn.cursor()
        today = datetime.date.today()
        first_day_of_current_month = today.replace(day=1)
        next_month = first_day_of_current_month.replace(day=28) + datetime.timedelta(
            days=4)
        first_day_of_next_month = next_month.replace(day=1)
        cursor.execute('''
            SELECT
                (SELECT IFNULL(SUM(amount), 0) FROM revenue WHERE date_received >= ? AND date_received < ?) AS revenue_current_month,
                (SELECT IFNULL(SUM(amount), 0) FROM expenses WHERE date_spent >= ? AND date_spent < ?) AS expenses_current_month
            ''', (
            first_day_of_current_month, first_day_of_next_month, first_day_of_current_month, first_day_of_next_month))
        current_month_data = cursor.fetchone()
        cursor.execute('''
            SELECT
                (SELECT IFNULL(SUM(amount), 0) FROM revenue) AS total_revenue,
                (SELECT IFNULL(SUM(amount), 0) FROM expenses) AS total_expenses
            ''')
        total_data = cursor.fetchone()
        summary = {
            'current_month': {
                'revenue': current_month_data[0],
                'expenses': current_month_data[1]
            },
            'total': {
                'revenue': total_data[0],
                'expenses': total_data[1]
            }
        }
        return summary
    except sqlite3.Error as e:
        print(e)
        return None


def get_all_materials(conn):
    """ Получить список всех материалов с их количествами """
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM inventory')
        materials = cursor.fetchall()
        return materials
    except sqlite3.Error as e:
        print(f"Ошибка при извлечении данных: {e}")
        return []
