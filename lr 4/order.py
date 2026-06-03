import uuid
from typing import List
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    COOKING = "cooking"
    READY = "ready"
    COMPLETED = "completed"


class OrderItem:
    """Елемент страви у замовленні."""
    
    # Константи бізнес-логіки
    MAX_QUANTITY_PER_ITEM = 20

    def __init__(self, name: str, price: float, quantity: int):
        if not name or not name.strip():
            raise ValueError("Назва страви не може бути порожньою.")
        if price <= 0:
            raise ValueError("Ціна страви повинна бути більшою за 0.")
        if quantity <= 0 or quantity > self.MAX_QUANTITY_PER_ITEM:
            raise ValueError(f"Кількість однієї страви повинна бути в межах від 1 до {self.MAX_QUANTITY_PER_ITEM}.")
        
        self.name = name.strip()
        self.price = Decimal(str(price))
        self.quantity = quantity


class Order:
    """Клас замовлення цифрового QR-меню."""
    
    # Константи бізнес-логіки
    MAX_TABLE_NUMBER = 50
    MAX_TIP_PERCENT = 50.0

    def __init__(self, table_number: int):
        if table_number <= 0 or table_number > self.MAX_TABLE_NUMBER:
            raise ValueError(f"Номер столика повинен бути в межах від 1 до {self.MAX_TABLE_NUMBER}.")
        
        self.id = uuid.uuid4()
        self.table_number = table_number
        self.items: List[OrderItem] = []
        self.status: OrderStatus = OrderStatus.PENDING
        self.discount_percent = Decimal('0')

    # Метод №1: Додавання страви до замовлення (Логіка циклів, умов та винятків)
    def add_item(self, name: str, price: float, quantity: int) -> None:
        if self.status != OrderStatus.PENDING:
            raise RuntimeError("Не можна редагувати замовлення, яке вже готується або виконано.")
        
        for item in self.items:
            if item.name == name.strip():
                new_qty = item.quantity + quantity
                # Використовуємо константу з класу OrderItem для уникнення дублювання
                if new_qty > OrderItem.MAX_QUANTITY_PER_ITEM:
                    raise ValueError(f"Сумарна кількість однієї страви не може перевищувати {OrderItem.MAX_QUANTITY_PER_ITEM}.")
                item.quantity = new_qty
                return
        
        self.items.append(OrderItem(name, price, quantity))

    # Метод №2: Застосування промокоду (Валідація та умовна логіка)
    def apply_promo_code(self, promo_code: str) -> None:
        if self.status != OrderStatus.PENDING:
            raise RuntimeError("Промокод можна застосувати тільки до нового замовлення.")
        
        valid_promos = {
            "SAVE10": Decimal('10'),
            "EATLOCAL": Decimal('15'),
            "VIP25": Decimal('25')
        }
        
        cleaned_code = promo_code.strip().upper()
        if cleaned_code not in valid_promos:
            raise ValueError(f"Недійсний або неіснуючий промокод: {promo_code}")
            
        self.discount_percent = valid_promos[cleaned_code]

    # Метод №3: Розрахунок фінальної вартості з чайовими та знижкою
    def calculate_total(self, tip_percent: float = 0.0) -> Decimal:
        if tip_percent < 0 or tip_percent > self.MAX_TIP_PERCENT:
            raise ValueError(f"Чайові повинні бути в діапазоні від 0% до {self.MAX_TIP_PERCENT}%.")
            
        if not self.items:
            return Decimal('0.00')  # Повертаємо точне значення Decimal

        subtotal = sum(item.price * item.quantity for item in self.items)
        
        if self.discount_percent > 0:
            subtotal -= subtotal * (self.discount_percent / Decimal('100'))
        
        tips = subtotal * (Decimal(str(tip_percent)) / Decimal('100'))
        total = subtotal + tips
        
        # Повертаємо чистий Decimal із правильним математичним округленням
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
