import sqlite3
import datetime
from datetime import datetime, timedelta
import pandas as pd


class DatabaseManager:
    def __init__(self, db_file):
        self.conn = self.create_connection(db_file)
        self.create_tables()

    def create_connection(self, db_file):
        """Создать соединение с базой данных SQLite, указанной в db_file"""
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except sqlite3.Error as e:
            print(e)
            return 0
        return conn

    def create_tables(self):
        """Создать все необходимые таблицы"""
        self.create_expenses_table()
        self.create_inventory_table()
        self.create_revenue_table()
        self.create_orders_table()
        return 1

    def create_expenses_table(self):
        """Создать таблицу для учёта расходов в базе данных"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    amount REAL,
                    date_spent TEXT,
                    description TEXT
                )
            ''')
            self.conn.commit()
            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def create_inventory_table(self):
        """Создать таблицу в базе данных для материалов"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    material_name TEXT PRIMARY KEY,
                    quantity INTEGER NOT NULL
                )
            ''')
            self.conn.commit()
            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def create_revenue_table(self):
        """Создать таблицу для учёта доходов в базе данных"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS revenue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    amount REAL,
                    date_received TEXT,
                    FOREIGN KEY(order_id) REFERENCES orders(id)
                )
            ''')
            self.conn.commit()
            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def create_orders_table(self):
        """Создать или обновить таблицу заказов в базе данных"""
        try:
            cursor = self.conn.cursor()
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
            self.conn.commit()
            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def update_material(self, material_name, amount, operation):
        """Обновить количество материала в базе данных"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT quantity FROM inventory WHERE material_name = ?', (material_name,))
            result = cursor.fetchone()

            if operation == 'add':
                if result:
                    new_quantity = result[0] + amount
                    cursor.execute('UPDATE inventory SET quantity = ? WHERE material_name = ?',
                                   (new_quantity, material_name))
                else:
                    cursor.execute('INSERT INTO inventory (material_name, quantity) VALUES (?, ?)',
                                   (material_name, amount))
            elif operation == 'subtract':
                if result and result[0] >= amount:
                    new_quantity = result[0] - amount
                    cursor.execute('UPDATE inventory SET quantity = ? WHERE material_name = ?',
                                   (new_quantity, material_name))
                else:
                    return -1
            self.conn.commit()
            return new_quantity if 'new_quantity' in locals() else amount
        except sqlite3.Error as e:
            print(e)
            return 0

    def add_order(self, name, link, material, material_amount, recommended_date, importance, settings, cost,
                  payment_info, done, creation_date):
        """Добавить новый заказ в базу данных"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO orders (name, link, material, material_amount, recommended_date, importance, settings, cost, payment_info, done, creation_date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, link, material, material_amount, recommended_date, importance, settings, cost, payment_info, done,
                creation_date))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(e)
            return -1

    def delete_unpaid_orders(self):
        """Удалить заказы, которые не были оплачены в течение 10 дней после создания"""
        try:
            cursor = self.conn.cursor()
            ten_days_ago = datetime.datetime.now() - datetime.timedelta(days=10)
            ten_days_ago_str = ten_days_ago.strftime('%Y-%m-%d')
            cursor.execute('''
                DELETE FROM orders 
                WHERE creation_date <= ? AND (payment_info = 0 OR payment_info IS NULL)
            ''', (ten_days_ago_str,))
            self.conn.commit()
            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def get_order_by_id(self, order_id):
        """Получить информацию о заказе по ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(e)
            return 0

    def delete_order(self, order_id):
        """Удалить заказ по ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
            self.conn.commit()
            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def add_revenue(self, order_id, amount, date_received):
        """Добавить запись о доходе от заказа"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO revenue (order_id, amount, date_received)
                VALUES (?, ?, ?)
            ''', (order_id, amount, date_received))
            self.conn.commit()
            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def add_expense(self, category, amount, date_spent, description):
        """Добавить запись о расходах"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO expenses (category, amount, date_spent, description)
                VALUES (?, ?, ?, ?)
            ''', (category, amount, date_spent, description))
            self.conn.commit()
            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def get_all_materials_excel(self, excel_path):
        """Экспортировать данные из таблицы inventory в файл Excel"""
        try:
            query = "SELECT * FROM inventory"
            df = pd.read_sql_query(query, self.conn)
            df.to_excel(excel_path, index=False)

            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def get_last_month_date_range(self):
        """Получить начало и конец последнего календарного месяца"""
        today = datetime.today()
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        return first_day_last_month, last_day_last_month

    def export_last_month_data_to_excel(self, excel_path):
        """Экспортировать данные расходов и доходов за последний календарный месяц в один файл Excel"""
        try:
            self.create_expenses_table()
            self.create_revenue_table()

            start_date, end_date = self.get_last_month_date_range()

            expenses_query = '''
                SELECT * FROM expenses
                WHERE date_spent BETWEEN ? AND ?
            '''
            revenue_query = '''
                SELECT * FROM revenue
                WHERE date_received BETWEEN ? AND ?
            '''

            expenses_df = pd.read_sql_query(expenses_query, self.conn,
                                            params=(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            revenue_df = pd.read_sql_query(revenue_query, self.conn,
                                           params=(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            with pd.ExcelWriter(excel_path) as writer:
                expenses_df.to_excel(writer, sheet_name='Expenses', index=False)
                revenue_df.to_excel(writer, sheet_name='Revenue', index=False)

            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def export_orders_to_excel(self, excel_path, done=True):
        try:
            query = '''
                SELECT * FROM orders
                WHERE done = ?
                ORDER BY recommended_date, importance DESC
            '''

            df = pd.read_sql_query(query, self.conn, params=(int(done),))

            sheet_name = 'Completed Orders' if done else 'Pending Orders'
            df.to_excel(excel_path, sheet_name=sheet_name, index=False)

            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def export_expenses_and_revenue_between_dates_to_excel(self, start_date, end_date, excel_path):
        """Получить расходы и доходы между указанными датами и сохранить их в Excel"""
        try:
            cursor = self.conn.cursor()

            expenses_query = "SELECT * FROM expenses WHERE date_spent BETWEEN ? AND ?"
            expenses_df = pd.read_sql_query(expenses_query, self.conn, params=(start_date, end_date))

            revenue_query = "SELECT * FROM revenue WHERE date_received BETWEEN ? AND ?"
            revenue_df = pd.read_sql_query(revenue_query, self.conn, params=(start_date, end_date))

            with pd.ExcelWriter(excel_path) as writer:
                expenses_df.to_excel(writer, sheet_name='Expenses', index=False)
                revenue_df.to_excel(writer, sheet_name='Revenue', index=False)

            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def auto_delete_expired_records(self, days):
        """Удалить записи из указанной таблицы, которые старше определенного количества дней"""
        try:
            cursor = self.conn.cursor()
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
            cursor.execute(f"DELETE FROM orders WHERE creation_date <= ?", (cutoff_date_str,))
            self.conn.commit()
            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def get_material_by_name(self, material_name):
        """Получить информацию о материале по названию"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM inventory WHERE material_name = ?', (material_name,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(e)
            return 0

    def get_expenses_by_category(self, category, excel_path):
        """Получить список расходов по категории и экспортировать в Excel"""
        try:
            cursor = self.conn.cursor()
            query = 'SELECT * FROM expenses WHERE category = ?'
            df = pd.read_sql_query(query, self.conn, params=(category,))
            df.to_excel(excel_path, index=False)
            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def update_order_status(self, order_id, done):
        """Обновить статус заказа по ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE orders SET done = ? WHERE id = ?', (done, order_id))
            self.conn.commit()
            return 1
        except sqlite3.Error as e:
            print(e)
            return 0

    def close_connection(self):
        """Закрыть соединение с базой данных"""
        if self.conn:
            self.conn.close()
            return 1
