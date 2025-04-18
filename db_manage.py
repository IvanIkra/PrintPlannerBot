import datetime
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import os


class DatabaseManager:
    def __init__(self, db_file: str):
        try:
            self.conn = self.create_connection(db_file)
            self.create_tables()
        except Exception as e:
            print(e)
            self.conn = None

    def create_connection(self, db_file: str):
        """Создать соединение с базой данных SQLite, указанной в db_file"""
        try:
            conn = sqlite3.connect(db_file)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Exception as e:
            print(e)
            return None

    def create_tables(self):
        """Создать все необходимые таблицы"""
        tables = [
            '''CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0
            )''',
            '''CREATE TABLE IF NOT EXISTS expense_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )''',
            '''CREATE TABLE IF NOT EXISTS order_statuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )''',
            '''CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                link TEXT,
                recommended_date TEXT,
                importance INTEGER,
                settings TEXT,
                cost REAL,
                payment_info BOOLEAN,
                status_id INTEGER NOT NULL DEFAULT 1,
                creation_date TEXT NOT NULL,
                FOREIGN KEY (status_id) REFERENCES order_statuses(id)
            )''',
            '''CREATE TABLE IF NOT EXISTS order_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                material_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (material_id) REFERENCES materials(id)
            )''',
            '''CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                date_spent TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (category_id) REFERENCES expense_categories(id)
            )''',
            '''CREATE TABLE IF NOT EXISTS revenue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                amount REAL,
                date_received TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            )'''
        ]
        
        try:
            cursor = self.conn.cursor()
            for table in tables:
                cursor.execute(table)
            
            # Initialize order statuses if empty
            cursor.execute("INSERT OR IGNORE INTO order_statuses (id, name) VALUES (1, 'pending'), (2, 'completed')")
            self.conn.commit()
            return 1
        except Exception as e:
            print(e)
            return 0

    def update_material(self, material_name: str, amount: int, operation: str):
        """Обновить количество материала в базе данных"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''INSERT OR IGNORE INTO materials (name, quantity) VALUES (?, 0)''', 
                         (material_name,))
            
            cursor.execute('SELECT quantity FROM materials WHERE name = ?', (material_name,))
            result = cursor.fetchone()
            
            match operation:
                case 'add':
                    new_quantity = result[0] + amount
                    cursor.execute('UPDATE materials SET quantity = ? WHERE name = ?',
                                 (new_quantity, material_name))
                case 'subtract':
                    if result[0] >= amount:
                        new_quantity = result[0] - amount
                        cursor.execute('UPDATE materials SET quantity = ? WHERE name = ?',
                                     (new_quantity, material_name))
                    else:
                        return -1
                case _:
                    raise ValueError("Invalid operation")
                    
            self.conn.commit()
            return new_quantity if 'new_quantity' in locals() else amount
        except Exception as e:
            print(e)
            return 0

    def add_order(self, name: str, link: str, material: str, material_amount: int, 
                 recommended_date: str, importance: int, settings: str, cost: float, 
                 payment_info: bool, done: bool, creation_date: str):
        """Добавить новый заказ в базу данных"""
        try:
            cursor = self.conn.cursor()
            status_id = 2 if done else 1
            
            # Add order
            cursor.execute('''
                INSERT INTO orders (name, link, recommended_date, importance, settings, 
                                  cost, payment_info, status_id, creation_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, link, recommended_date, importance, settings, cost, 
                 payment_info, status_id, creation_date))
            
            order_id = cursor.lastrowid
            
            # Ensure material exists and add order_materials relation
            cursor.execute('INSERT OR IGNORE INTO materials (name, quantity) VALUES (?, 0)',
                         (material,))
            cursor.execute('SELECT id FROM materials WHERE name = ?', (material,))
            material_id = cursor.fetchone()[0]
            
            cursor.execute('''
                INSERT INTO order_materials (order_id, material_id, quantity)
                VALUES (?, ?, ?)
            ''', (order_id, material_id, material_amount))
            
            self.conn.commit()
            return order_id
        except Exception as e:
            print(e)
            return -1

    def delete_unpaid_orders(self):
        """Удалить заказы, которые не были оплачены в течение 10 дней после создания"""
        try:
            cursor = self.conn.cursor()
            ten_days_ago = datetime.now() - timedelta(days=10)
            ten_days_ago_str = ten_days_ago.strftime('%Y-%m-%d')
            cursor.execute('''
                DELETE FROM orders 
                WHERE creation_date <= ? AND (payment_info = 0 OR payment_info IS NULL)
            ''', (ten_days_ago_str,))
            self.conn.commit()
            return 1
        except Exception as e:
            print(e)
            return 0

    def get_order(self, info: str, key: str = 'id'):
        """Получить информацию о заказе по ID"""
        try:
            cursor = self.conn.cursor()
            if key == 'id':
                query = '''
                    SELECT o.*, m.name as material, om.quantity as material_amount 
                    FROM orders o
                    LEFT JOIN order_materials om ON o.id = om.order_id
                    LEFT JOIN materials m ON om.material_id = m.id
                    WHERE o.id = ?
                '''
            else:
                query = '''
                    SELECT o.*, m.name as material, om.quantity as material_amount 
                    FROM orders o
                    LEFT JOIN order_materials om ON o.id = om.order_id
                    LEFT JOIN materials m ON om.material_id = m.id
                    WHERE o.name = ?
                '''
            cursor.execute(query, (info,))
            return cursor.fetchone()
        except Exception as e:
            print(e)
            return 0

    def delete_order(self, order_id: int):
        """Удалить заказ по ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
            self.conn.commit()
            return 1
        except Exception as e:
            print(e)
            return 0

    def add_revenue(self, order_id: int, amount: float, date_received: str):
        """Добавить запись о доходе от заказа"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO revenue (order_id, amount, date_received)
                VALUES (?, ?, ?)
            ''', (order_id, amount, date_received))
            self.conn.commit()
            return 1
        except Exception as e:
            print(e)
            return 0

    def add_expense(self, category: str, amount: float, date_spent: str, description: str):
        """Добавить запись о расходах"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO expense_categories (name) VALUES (?)',
                         (category,))
            cursor.execute('SELECT id FROM expense_categories WHERE name = ?', (category,))
            category_id = cursor.fetchone()[0]
            
            cursor.execute('''
                INSERT INTO expenses (category_id, amount, date_spent, description)
                VALUES (?, ?, ?, ?)
            ''', (category_id, amount, date_spent, description))
            
            self.conn.commit()
            return 1
        except Exception as e:
            print(e)
            return 0

    def get_all_materials_excel(self, excel_path: str):
        """Экспортировать данные из таблицы inventory в файл Excel"""
        try:
            query = "SELECT * FROM inventory"
            df = pd.read_sql_query(query, self.conn)
            df.to_excel(excel_path, index=False)

            return 1
        except Exception as e:
            print(e)
            return 0

    def get_last_month_date_range(self):
        """Получить начало и конец последнего календарного месяца"""
        try:
            today = datetime.today()
            first_day_this_month = today.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            first_day_last_month = last_day_last_month.replace(day=1)
            return first_day_last_month, last_day_last_month
        except Exception as e:
            print(e)
            return None, None

    def export_last_month_data_to_excel(self, excel_path: str):
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
        except Exception as e:
            print(e)
            return 0

    def export_orders_to_excel(self, excel_path: str, done: bool=True):
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
        except Exception as e:
            print(e)
            return 0

    def export_expenses_and_revenue_between_dates_to_excel(self, start_date: str, end_date: str, excel_path: str):
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
        except Exception as e:
            print(e)
            return 0

    def auto_delete_expired_records(self, days: int):
        """Удалить записи из указанной таблицы, которые старше определенного количества дней"""
        try:
            cursor = self.conn.cursor()
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
            cursor.execute(f"DELETE FROM orders WHERE creation_date <= ?", (cutoff_date_str,))
            self.conn.commit()
            return 1
        except Exception as e:
            print(e)
            return 0

    def get_material_by_name(self, material_name: str):
        """Получить информацию о материале по названию"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT name, quantity FROM materials WHERE name = ?', 
                         (material_name,))
            return cursor.fetchone()
        except Exception as e:
            print(e)
            return 0

    def get_expenses_by_category(self, category: str, excel_path: str):
        """Получить список расходов по категории и экспортировать в Excel"""
        try:
            cursor = self.conn.cursor()
            query = '''
                SELECT e.amount, e.date_spent, e.description 
                FROM expenses e
                JOIN expense_categories ec ON e.category_id = ec.id
                WHERE ec.name = ?
            '''
            df = pd.read_sql_query(query, self.conn, params=(category,))
            df.to_excel(excel_path, index=False)
            return 1
        except Exception as e:
            print(e)
            return 0

    def update_order_status(self, order_id: int, done: bool):
        """Обновить статус заказа по ID"""
        try:
            cursor = self.conn.cursor()
            status_id = 2 if done else 1
            cursor.execute('UPDATE orders SET status_id = ? WHERE id = ?', 
                         (status_id, order_id))
            self.conn.commit()
            return 1
        except Exception as e:
            print(e)
            return 0

    def close_connection(self):
        """Закрыть соединение с базой данных"""
        try:
            if self.conn:
                self.conn.close()
                return 1
            return 0
        except Exception as e:
            print(e)
            return 0
