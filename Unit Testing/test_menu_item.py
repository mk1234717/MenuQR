import pytest
from menu_item import MenuItem, SeasonalDiscount, ValidationResult

# ----------------------------------------------------------------------
# Тести для методу calculate_final_price
# ----------------------------------------------------------------------

def test_calculate_final_price_available_no_discount():
    """EP: доступна страва без знижок -> повертає базову ціну"""
    # Arrange
    item = MenuItem(name="Борщ", price=100.0, is_available=True)
    # Act
    result = item.calculate_final_price(active_discounts=None)
    # Assert
    assert result == 100.0

def test_calculate_final_price_unavailable():
    """EP: недоступна страва -> виняток RuntimeError"""
    # Arrange
    item = MenuItem(name="Борщ", price=100.0, is_available=False)
    # Act & Assert
    with pytest.raises(RuntimeError, match="Страва 'Борщ' недоступна"):
        item.calculate_final_price()

def test_calculate_final_price_special_discount_25():
    """EP: спеціальна знижка 25% -> ціна зменшується на 25%"""
    # Arrange
    item = MenuItem(name="Борщ", price=200.0, special_discount_percent=25.0)
    # Act
    result = item.calculate_final_price()
    # Assert
    assert result == 150.0

def test_calculate_final_price_special_discount_boundaries():
    """BVA: перевірка граничних значень знижки 0% та 100%"""
    # Arrange
    item0 = MenuItem(name="Страва0", price=100.0, special_discount_percent=0)
    item100 = MenuItem(name="Страва100", price=100.0, special_discount_percent=100)
    # Act
    result0 = item0.calculate_final_price()
    result100 = item100.calculate_final_price()
    # Assert
    assert result0 == 100.0
    assert result100 == 0.0

def test_calculate_final_price_multiple_seasonal_discounts():
    """EP: цикл – кілька сезонних знижок, що застосовуються"""
    # Arrange
    item = MenuItem(name="Страва", price=100.0)
    disc1 = SeasonalDiscount("Sale1", 10, lambda m: True)
    disc2 = SeasonalDiscount("Sale2", 20, lambda m: True)
    # Act
    result = item.calculate_final_price(active_discounts=[disc1, disc2])
    # Assert
    # 100 * 0.9 * 0.8 = 72.0
    assert result == 72.0

# ----------------------------------------------------------------------
# Тести для методу calculate_price_with_vat
# ----------------------------------------------------------------------

def test_calculate_price_with_vat_standard():
    """EP: ставка ПДВ 20% -> ціна збільшується на 20%"""
    # Arrange
    item = MenuItem(name="Страва", price=100.0)
    # Act
    result = item.calculate_price_with_vat("standard_20")
    # Assert
    assert result == 120.00

def test_calculate_price_with_vat_reduced():
    """EP: ставка ПДВ 7% -> ціна збільшується на 7%"""
    # Arrange
    item = MenuItem(name="Страва", price=100.0)
    # Act
    result = item.calculate_price_with_vat("reduced_7")
    # Assert
    assert result == 107.00

def test_calculate_price_with_vat_invalid_rate():
    """EP: невідома ставка ПДВ -> виняток ValueError"""
    # Arrange
    item = MenuItem(name="Страва", price=100.0)
    # Act & Assert
    with pytest.raises(ValueError, match="Невідома ставка ПДВ"):
        item.calculate_price_with_vat("unknown")

def test_calculate_price_with_vat_price_boundaries():
    """BVA: перевірка граничних значень ціни (0 та 0.01)"""
    # Arrange
    item_zero = MenuItem(name="Нуль", price=0.0)
    item_small = MenuItem(name="Мала", price=0.01)
    # Act
    result_zero = item_zero.calculate_price_with_vat("standard_20")
    result_small = item_small.calculate_price_with_vat("standard_20")
    # Assert
    assert result_zero == 0.0
    assert result_small == 0.01  # 0.01 * 1.20 = 0.012 -> округлення до 0.01

# ----------------------------------------------------------------------
# Тести для методу validate_for_publish
# ----------------------------------------------------------------------

def test_validate_for_publish_valid():
    """EP: всі поля коректні -> is_valid = True"""
    # Arrange
    item = MenuItem(
        name="Піца",
        price=150.0,
        image_url="https://example.com/pizza.jpg"
    )
    # Act
    result = item.validate_for_publish()
    # Assert
    assert result.is_valid is True
    assert result.errors == []

def test_validate_for_publish_name_boundaries():
    """BVA: перевірка границь довжини назви (1, 2, 100, 101 символів)"""
    # Тест для назви з 1 символу (невалідно)
    item1 = MenuItem(name="A", price=100.0)
    result1 = item1.validate_for_publish()
    assert result1.is_valid is False
    assert any("хоча б 2 символи" in err for err in result1.errors)

    # Тест для назви з 2 символів (валідно)
    item2 = MenuItem(name="AB", price=100.0)
    result2 = item2.validate_for_publish()
    # Інші поля валідні? Ціна 100 >0, знижки немає – має бути valid
    assert result2.is_valid is True

    # Тест для назви зі 100 символів (валідно)
    name100 = "X" * 100
    item100 = MenuItem(name=name100, price=100.0)
    result100 = item100.validate_for_publish()
    assert result100.is_valid is True

    # Тест для назви з 101 символу (невалідно)
    name101 = "X" * 101
    item101 = MenuItem(name=name101, price=100.0)
    result101 = item101.validate_for_publish()
    assert result101.is_valid is False
    assert any("не може перевищувати 100" in err for err in result101.errors)

def test_validate_for_publish_price_boundaries():
    """BVA: перевірка границь ціни (0, 10000.01, від'ємна)"""
    # Ціна = 0 (невалідно через конструктор? Конструктор price=0 дозволяє, але валідація забороняє)
    item_zero = MenuItem(name="Десерт", price=0.0)
    result_zero = item_zero.validate_for_publish()
    assert result_zero.is_valid is False
    assert any("не може дорівнювати нулю" in err for err in result_zero.errors)

    # Ціна > 10000 (невалідно)
    item_high = MenuItem(name="Люкс", price=10000.01)
    result_high = item_high.validate_for_publish()
    assert result_high.is_valid is False
    assert any("Ціна занадто висока" in err for err in result_high.errors)

    # Від'ємна ціна – перевіряємо, що конструктор кидає ValueError (не доходимо до validate_for_publish)
    with pytest.raises(ValueError, match="Ціна не може бути від'ємною"):
        MenuItem(name="Помилка", price=-0.01)


# ----------------------------------------------------------------------
# Додаткові тести для досягнення 100% покриття (ітеративний цикл)
# ----------------------------------------------------------------------

def test_calculate_final_price_negative_protection():
    """Перевірка захисної логіки: якщо сумарна знижка >100% -> ціна стає 0"""
    # Arrange: створюємо страву з ціною 100, спеціальною знижкою 80%
    item = MenuItem(name="Тест", price=100.0, special_discount_percent=80.0)
    # Сезонна знижка 50% (разом 130% знижки)
    disc = SeasonalDiscount("Super", 50, lambda m: True)
    # Act
    result = item.calculate_final_price(active_discounts=[disc])
    # Assert: ціна має стати 0, а не від'ємною
    assert result == 0.0


def test_calculate_final_price_rounding():
    """BVA: перевірка округлення до 2 знаків (наприклад, 0.005 -> 0.01)"""
    # Arrange
    item = MenuItem(name="Кава", price=0.03, special_discount_percent=33.33)
    # 0.03 * (1 - 0.3333) = 0.03 * 0.6667 = 0.020001 -> округлення до 0.02
    # Але точніше: Decimal('0.03') * (Decimal('66.67')/100) = ?
    # Спростимо: price=0.07, знижка 50% -> 0.035 -> округлення до 0.04
    item2 = MenuItem(name="Чай", price=0.07, special_discount_percent=50.0)
    # Act
    result = item2.calculate_final_price()
    # Assert: 0.07 * 0.5 = 0.035 -> округлюється до 0.04 (bankers rounding? Python ROUND_HALF_UP)
    assert result == 0.04


def test_validate_for_publish_discount_100_percent():
    """EP: спеціальна знижка 100% при ціні >0 -> невалідно"""
    # Arrange
    item = MenuItem(name="Безкоштовно?", price=50.0, special_discount_percent=100.0)
    # Act
    result = item.validate_for_publish()
    # Assert
    assert result.is_valid is False
    assert any("безкоштовною" in err for err in result.errors)


def test_validate_for_publish_invalid_image_url():
    """EP: некоректний URL зображення -> помилка"""
    # Arrange
    item = MenuItem(
        name="Страва",
        price=100.0,
        image_url="ftp://not-http-url.com"
    )
    # Act
    result = item.validate_for_publish()
    # Assert
    assert result.is_valid is False
    assert any("коректним URL" in err for err in result.errors)


def test_constructor_price_exceeds_maximum():
    """BVA: ціна більше 1_000_000 -> виняток"""
    with pytest.raises(ValueError, match="перевищує максимально допустиму"):
        MenuItem(name="Дорого", price=1_000_001.0)


def test_constructor_price_at_maximum():
    """BVA: ціна дорівнює 1_000_000 -> допустимо"""
    item = MenuItem(name="Максимум", price=1_000_000.0)
    assert item.price == 1_000_000.0


def test_set_availability():
    """Позитивний тест для допоміжного методу set_availability (покриття рядків)"""
    item = MenuItem(name="Страва", price=100.0)
    assert item.is_available is True  # за замовчуванням
    item.set_availability(False)
    assert item.is_available is False
    item.set_availability(True)
    assert item.is_available is True


def test_set_special_discount():
    """Позитивний та негативний тести для set_special_discount"""
    item = MenuItem(name="Страва", price=100.0)
    item.set_special_discount(25.0)
    assert item.special_discount_percent == 25.0

    item.set_special_discount(None)
    assert item.special_discount_percent is None

    # Негативний: знижка >100
    with pytest.raises(ValueError, match="Знижка має бути в межах 0–100"):
        item.set_special_discount(150.0)

    with pytest.raises(ValueError, match="Знижка має бути в межах 0–100"):
        item.set_special_discount(-10.0)