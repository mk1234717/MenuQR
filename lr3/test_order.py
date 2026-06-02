import pytest
from pytest import approx
from order import Order, OrderItem, OrderStatus

# --- Тести методу add_item ---

def test_add_item_success():
    """EP: Успішне додавання нової страви у замовлення."""
    # Arrange
    order = Order(table_number=5)
    
    # Act
    order.add_item(name="Піца", price=180.0, quantity=2)
    
    # Assert
    assert len(order.items) == 1
    assert order.items[0].name == "Піца"
    assert order.items[0].quantity == 2

def test_add_item_wrong_status():
    """EP: Спроба зміни замовлення у невідповідному статусі -> RuntimeError."""
    # Arrange
    order = Order(table_number=5)
    order.status = OrderStatus.COOKING
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Не можна редагувати замовлення"):
        order.add_item(name="Піца", price=180.0, quantity=1)

def test_add_item_quantity_boundaries():
    """BVA: Перевірка меж кількості страв (1, 20, 21)."""
    order = Order(table_number=1)
    
    # Межа 1 - успішно
    order.add_item("Сік", 40.0, 1)
    assert order.items[0].quantity == 1
    
    # Межа 20 - успішно для нового елементу
    order.add_item("Кава", 50.0, 20)
    assert order.items[1].quantity == 20
    
    # Межа 21 (або накопичення > 20) -> ValueError
    with pytest.raises(ValueError, match="кількість однієї страви не може перевищувати 20"):
        order.add_item("Кава", 50.0, 1)

# --- Тести методу apply_promo_code ---

def test_apply_promo_code_valid():
    """EP: Валідний промокод встановлює правильну знижку."""
    # Arrange
    order = Order(table_number=12)
    
    # Act
    order.apply_promo_code("EATLOCAL")
    
    # Assert
    assert order.discount_percent == 15

def test_apply_promo_code_invalid():
    """EP: Невалідний промокод викликає виняток ValueError."""
    # Arrange
    order = Order(table_number=12)
    
    # Act & Assert
    with pytest.raises(ValueError, match="Недійсний або неіснуючий промокод"):
        order.apply_promo_code("INVALID_CODE")

# --- Тести методу calculate_total ---

def test_calculate_total_empty():
    """EP: Розрахунок суми для порожнього замовлення рівний 0."""
    # Arrange
    order = Order(table_number=3)
    
    # Act
    total = order.calculate_total()
    
    # Assert
    assert total == approx(0.0)

def test_calculate_total_with_discount_and_tips():
    """EP: Комплексний розрахунок вартості зі знижкою та чайовими."""
    # Arrange
    order = Order(table_number=3)
    order.add_item("Борщ", 100.0, 2)  # 200.0
    order.apply_promo_code("SAVE10")   # -10% -> 180.0
    
    # Act
    total = order.calculate_total(tip_percent=10.0) 
    
    # Assert
    assert total == approx(198.0)

def test_calculate_total_tip_boundaries():
    """BVA: Перевірка меж відсотків чайових (0%, 50%, -0.01%, 50.01%)."""
    order = Order(table_number=2)
    order.add_item("Стейк", 500.0, 1)
    
    # Нижня межа 0%
    assert order.calculate_total(tip_percent=0.0) == approx(500.0)
    
    # Верхня межа 50%
    assert order.calculate_total(tip_percent=50.0) == approx(750.0)
    
    # Поза нижньою межею
    with pytest.raises(ValueError, match="Чайові повинні бути в діапазоні"):
        order.calculate_total(tip_percent=-0.01)
        
    # Поза верхньою межею
    with pytest.raises(ValueError, match="Чайові повинні бути в діапазоні"):
        order.calculate_total(tip_percent=50.01)

def test_order_item_invalid_name():
    """EP/Негативний: Створення елемента замовлення без назви."""
    with pytest.raises(ValueError, match="Назва страви не може бути порожньою"):
        OrderItem(name="   ", price=10.0, quantity=1)

def test_order_invalid_table():
    """BVA/Негативний: Некоректний номер столика (0 або 51)."""
    with pytest.raises(ValueError, match="Номер столика повинен бути в межах"):
        Order(table_number=0)
