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

    def create_connection(self, db_file: str) -> sqlite3.Connection | None:
        """Создать соединение с базой данных SQLite, указанной в db_file"""
        try:
            conn = sqlite3.connect(db_file)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Exception as e:
            print(e)
            return None

    def create_tables(self) -> int:
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

    def update_material(self, material_name: str, amount: int, operation: str) -> int | float:
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
                 payment_info: bool, done: bool, creation_date: str) -> int:
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

    def get_pending_orders(self) -> list:
        """Получить все невыполненные заказы"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT 
                    o.id,
                    o.name,
                    o.link,
                    m.name as material,
                    om.quantity as material_amount,
                    o.recommended_date,
                    o.importance,
                    o.settings,
                    o.cost,
                    o.creation_date
                FROM orders o
                LEFT JOIN order_materials om ON o.id = om.order_id
                LEFT JOIN materials m ON om.material_id = m.id
                WHERE o.status_id = 1
                ORDER BY o.recommended_date, o.importance DESC
            ''')
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting pending orders: {e}")
            return []

    def export_pending_orders_to_excel(self, excel_path: str) -> bool:
        """Экспортировать невыполненные заказы в Excel"""
        try:
            orders = self.get_pending_orders()
            
            if not orders:
                return False
                
            columns = ['ID', 'Название', 'Ссылка', 'Материал', 'Количество материала', 
                    'Дата выполнения', 'Важность', 'Настройки', 'Стоимость', 'Дата создания']
            df = pd.DataFrame(orders, columns=columns)
            
            # Сортировка по ID
            df = df.sort_values('ID')
            
            # Создаем директорию для excel файла, если её нет
            os.makedirs(os.path.dirname(excel_path), exist_ok=True)
            
            # Создаем writer с engine='xlsxwriter' для форматирования
            with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Невыполненные заказы')
                
                # Получаем workbook и worksheet
                workbook = writer.book
                worksheet = writer.sheets['Невыполненные заказы']
                
                # Форматы для заголовков и данных
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'vcenter',
                    'align': 'center',
                    'border': 1,
                    'bg_color': '#D9D9D9'  # Светло-серый фон для заголовков
                })
                
                data_format = workbook.add_format({
                    'align': 'left',
                    'valign': 'vcenter',
                    'border': 1
                })
                
                # Применяем форматы к заголовкам
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Применяем форматы к данным
                for row in range(len(df)):
                    for col in range(len(df.columns)):
                        worksheet.write(row + 1, col, df.iloc[row, col], data_format)
                
                # Автоматическая настройка ширины столбцов
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),  # максимальная длина данных
                        len(col)  # длина заголовка
                    )
                    worksheet.set_column(idx, idx, max_length + 2)
                
                # Устанавливаем высоту строк
                worksheet.set_default_row(20)  # Высота для всех строк
                worksheet.set_row(0, 25)  # Увеличенная высота для заголовка
                
            return True
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False

    def delete_unpaid_orders(self) -> int:
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

    def get_order(self, info: str, key: str = 'id') -> tuple | int:
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

    def delete_order(self, order_id: int) -> int:
        """Удалить заказ по ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
            self.conn.commit()
            return 1
        except Exception as e:
            print(e)
            return 0

    def add_revenue(self, order_id: int, amount: float, date_received: str) -> int:
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

    def add_expense(self, category: str, amount: float, date_spent: str, description: str) -> int:
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

    def auto_delete_expired_records(self, days: int) -> int:
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

    def get_material_by_name(self, material_name: str) -> tuple | int:
        """Получить информацию о материале по названию"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT name, quantity FROM materials WHERE name = ?', 
                         (material_name,))
            return cursor.fetchone()
        except Exception as e:
            print(e)
            return 0

    def update_order_status(self, order_id: int, done: bool) -> int:
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

    def close_connection(self) -> int:
        """Закрыть соединение с базой данных"""
        try:
            if self.conn:
                self.conn.close()
                return 1
            return 0
        except Exception as e:
            print(e)
            return 0

    def get_all_materials(self) -> list[tuple] | int:
        """Получить список всех материалов из базы данных"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT name, quantity FROM materials')
            return cursor.fetchall()
        except Exception as e:
            print(e)
            return 0

    def update_order_cost(self, order_id: int, cost: float) -> bool:
        """Обновить стоимость заказа"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE orders SET cost = ? WHERE id = ?', (cost, order_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating order cost: {e}")
            return False
        