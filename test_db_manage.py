import pytest
import os
from datetime import datetime, timedelta
from db_manage import DatabaseManager


@pytest.fixture
def db_manager():
    test_db = 'test_database.db'
    manager = DatabaseManager(test_db)
    yield manager
    manager.close_connection()
    if os.path.exists(test_db):
        os.remove(test_db)


def test_create_tables(db_manager):
    cursor = db_manager.conn.cursor()
    
    tables = [
        'materials',
        'expense_categories',
        'order_statuses',
        'orders',
        'order_materials',
        'expenses',
        'revenue'
    ]
    
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        assert cursor.fetchone() is not None


def test_update_material(db_manager):
    material_name = 'TestMaterial'
    
    # Test adding material
    result = db_manager.update_material(material_name, 50, 'add')
    assert result == 50
    
    # Test adding more to existing material
    result = db_manager.update_material(material_name, 30, 'add')
    assert result == 80
    
    # Test successful subtraction
    result = db_manager.update_material(material_name, 30, 'subtract')
    assert result == 50
    
    # Test failed subtraction (not enough material)
    result = db_manager.update_material(material_name, 100, 'subtract')
    assert result == -1


def test_add_and_get_order(db_manager):
    order_data = {
        'name': 'TestOrder',
        'link': 'http://test.com',
        'material': 'TestMaterial',
        'material_amount': 10,
        'recommended_date': '2024-12-01',
        'importance': 1,
        'settings': 'Test Settings',
        'cost': 100.0,
        'payment_info': True,
        'done': False,
        'creation_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Test adding order
    order_id = db_manager.add_order(**order_data)
    assert order_id > 0
    
    # Test getting order by id
    order = db_manager.get_order(order_id)
    assert order is not None
    assert order[1] == order_data['name']  # Check name
    assert order[2] == order_data['link']  # Check link
    
    # Test getting order by name
    order = db_manager.get_order(order_data['name'], key='name')
    assert order is not None
    assert order[1] == order_data['name']


def test_add_and_get_expense(db_manager):
    expense_data = {
        'category': 'TestCategory',
        'amount': 50.0,
        'date_spent': datetime.now().strftime('%Y-%m-%d'),
        'description': 'Test expense'
    }
    
    # Test adding expense
    result = db_manager.add_expense(**expense_data)
    assert result == 1
    
    # Test getting expenses by category
    test_excel = 'test_expenses.xlsx'
    result = db_manager.get_expenses_by_category(expense_data['category'], test_excel)
    assert result == 1
    assert os.path.exists(test_excel)
    os.remove(test_excel)


def test_update_order_status(db_manager):
    # First create an order
    order_data = {
        'name': 'StatusTestOrder',
        'link': 'http://test.com',
        'material': 'TestMaterial',
        'material_amount': 10,
        'recommended_date': '2024-12-01',
        'importance': 1,
        'settings': 'Test Settings',
        'cost': 100.0,
        'payment_info': True,
        'done': False,
        'creation_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    order_id = db_manager.add_order(**order_data)
    
    # Test updating status
    result = db_manager.update_order_status(order_id, True)
    assert result == 1
    
    # Verify status was updated
    order = db_manager.get_order(order_id)
    assert order is not None
    assert order[8] == 2  # status_id should be 2 for completed


def test_get_material_by_name(db_manager):
    material_name = 'TestMaterial'
    
    # First add some material
    db_manager.update_material(material_name, 50, 'add')
    
    # Test getting material
    material = db_manager.get_material_by_name(material_name)
    assert material is not None
    assert material[0] == material_name
    assert material[1] == 50


def test_error_handling(db_manager):
    # Test invalid material operation
    result = db_manager.update_material('TestMaterial', 50, 'invalid_operation')
    assert result == 0
    
    # Test getting non-existent order
    result = db_manager.get_order(999999)
    assert result is None or result == 0
    
    # Test getting non-existent material
    result = db_manager.get_material_by_name('NonExistentMaterial')
    assert result is None or result == 0


def test_database_connection(db_manager):
    # Test connection is active
    assert db_manager.conn is not None
    
    # Test closing connection
    result = db_manager.close_connection()
    assert result == 1


def test_invalid_db_connection():
    invalid_path = '/invalid/path/db.db'
    manager = DatabaseManager(invalid_path)
    assert manager.conn is None


def test_multiple_material_operations(db_manager):
    material_name = 'TestMaterial'
    
    # Test sequence of operations
    operations = [
        ('add', 50, 50),
        ('add', 30, 80),
        ('subtract', 20, 60),
        ('add', 0, 60),
        ('subtract', 60, 0),
        ('subtract', 1, -1)
    ]
    
    for op, amount, expected in operations:
        result = db_manager.update_material(material_name, amount, op)
        assert result == expected


def test_order_edge_cases(db_manager):
    # Test empty strings
    order_data = {
        'name': '',
        'link': '',
        'material': '',
        'material_amount': 0,
        'recommended_date': '',
        'importance': 0,
        'settings': '',
        'cost': 0.0,
        'payment_info': False,
        'done': False,
        'creation_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    order_id = db_manager.add_order(**order_data)
    assert order_id > 0
    
    # Test very large values
    order_data.update({
        'name': 'Large Order',
        'material_amount': 999999999,
        'importance': 999999999,
        'cost': 999999999.99
    })
    
    order_id = db_manager.add_order(**order_data)
    assert order_id > 0


def test_expense_edge_cases(db_manager):
    test_cases = [
        # Empty strings
        {
            'category': '',
            'amount': 0,
            'date_spent': datetime.now().strftime('%Y-%m-%d'),
            'description': ''
        },
        # Very large amount
        {
            'category': 'Large Expense',
            'amount': 999999999.99,
            'date_spent': datetime.now().strftime('%Y-%m-%d'),
            'description': 'Very large expense'
        },
        # Special characters in category
        {
            'category': '!@#$%^&*()',
            'amount': 100,
            'date_spent': datetime.now().strftime('%Y-%m-%d'),
            'description': 'Special characters test'
        }
    ]
    
    for case in test_cases:
        result = db_manager.add_expense(**case)
        assert result == 1


def test_date_handling(db_manager):
    dates = [
        '2024-01-01',
        '2024-12-31',
        '2024-02-29',  # Leap year
        datetime.now().strftime('%Y-%m-%d'),
        (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    ]
    
    for date in dates:
        order_data = {
            'name': f'Date Test {date}',
            'link': 'http://test.com',
            'material': 'TestMaterial',
            'material_amount': 10,
            'recommended_date': date,
            'importance': 1,
            'settings': 'Test Settings',
            'cost': 100.0,
            'payment_info': True,
            'done': False,
            'creation_date': date
        }
        
        order_id = db_manager.add_order(**order_data)
        assert order_id > 0


def test_concurrent_operations(db_manager):
    material_name = 'ConcurrentMaterial'
    
    # Add initial quantity
    db_manager.update_material(material_name, 100, 'add')
    
    # Simulate concurrent operations
    operations = [
        ('add', 50),
        ('subtract', 30),
        ('add', 20),
        ('subtract', 40)
    ]
    
    for op, amount in operations:
        result = db_manager.update_material(material_name, amount, op)
        assert result > -1
    
    # Verify final quantity
    material = db_manager.get_material_by_name(material_name)
    assert material is not None
    assert material[1] == 100  # Initial 100 + 50 - 30 + 20 - 40 = 100


def test_duplicate_materials(db_manager):
    material_name = 'DuplicateMaterial'
    
    # Try to add same material multiple times
    for _ in range(5):
        result = db_manager.update_material(material_name, 10, 'add')
        assert result > 0
    
    # Verify only one record exists
    material = db_manager.get_material_by_name(material_name)
    assert material is not None
    assert material[1] == 50  # 5 * 10


def test_order_status_transitions(db_manager):
    # Create order
    order_data = {
        'name': 'StatusTest',
        'link': 'http://test.com',
        'material': 'TestMaterial',
        'material_amount': 10,
        'recommended_date': '2024-12-01',
        'importance': 1,
        'settings': 'Test Settings',
        'cost': 100.0,
        'payment_info': True,
        'done': False,
        'creation_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    order_id = db_manager.add_order(**order_data)
    
    # Test status transitions
    transitions = [
        (True, 2),   # pending -> completed
        (False, 1),  # completed -> pending
        (True, 2),   # pending -> completed
    ]
    
    for new_status, expected_status_id in transitions:
        result = db_manager.update_order_status(order_id, new_status)
        assert result == 1
        
        order = db_manager.get_order(order_id)
        assert order is not None
        assert order[8] == expected_status_id


def test_excel_export_formats(db_manager):
    # Add test data
    db_manager.add_expense('TestCategory', 100, datetime.now().strftime('%Y-%m-%d'), 'Test')
    
    # Test different Excel file paths
    test_paths = [
        'test.xlsx',
        'test_expenses.xlsx',
        'test_dir/test.xlsx'
    ]
    
    for path in test_paths:
        dir_name = os.path.dirname(path)
        if dir_name:  # Create directory only if path contains directory
            os.makedirs(dir_name, exist_ok=True)
        
        result = db_manager.get_expenses_by_category('TestCategory', path)
        assert result == 1
        assert os.path.exists(path)
        
        # Cleanup
        os.remove(path)
        if dir_name:
            os.rmdir(dir_name)


def test_database_cleanup(db_manager):
    # Add some test data
    db_manager.add_order(
        'TestOrder', 'http://test.com', 'TestMaterial', 10,
        '2024-12-01', 1, 'Test Settings', 100.0, True, False,
        datetime.now().strftime('%Y-%m-%d')
    )
    
    # Close connection
    result = db_manager.close_connection()
    assert result == 1
    
    # Try operations after closing - should return 0 instead of raising exception
    result = db_manager.get_order(1)
    assert result == 0