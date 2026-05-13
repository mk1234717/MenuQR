import uuid
from typing import List, Optional, Callable
from decimal import Decimal, ROUND_HALF_UP

class SeasonalDiscount:
    """DTO для сезонних/акційних знижок."""
    def __init__(self, name: str, percent: float, applies_to: Callable[['MenuItem'], bool]):
        self.name = name
        self.percent = percent  # 0-100
        self.applies_to = applies_to

class ValidationResult:
    """Результат валідації."""
    def __init__(self, is_valid: bool = True, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []

class MenuItem:
    """
    Страва в меню закладу.
    Відповідає діаграмі класів з ЛР 02 + розширений для unit-тестування.
    """

    def __init__(self, name: str, price: float, image_url: str = None,
                 is_available: bool = True, special_discount_percent: Optional[float] = None):
        """
        Конструктор з валідацією (обробка виняткових ситуацій).
        """
        if not name or not name.strip():
            raise ValueError("Назва страви не може бути порожньою.")
        if price < 0:
            raise ValueError("Ціна не може бути від'ємною.")
        if price > 1_000_000:
            raise ValueError("Ціна перевищує максимально допустиму (1 000 000).")
        if special_discount_percent is not None and (special_discount_percent < 0 or special_discount_percent > 100):
            raise ValueError("Знижка має бути в діапазоні 0–100%.")

        self.id = uuid.uuid4()
        self.name = name.strip()
        self.price = Decimal(str(price))
        self.image_url = image_url or ""
        self.is_available = is_available
        self.special_discount_percent = Decimal(str(special_discount_percent)) if special_discount_percent is not None else None

    # ----------------------------------------------------------------------
    # Метод №1 (нетривіальний): Розрахунок фінальної ціни зі знижками
    # ----------------------------------------------------------------------
    def calculate_final_price(self, active_discounts: Optional[List[SeasonalDiscount]] = None) -> float:
        """
        Повертає ціну після застосування спеціальної знижки та всіх активних сезонних акцій.
        - Якщо страва недоступна -> виняток.
        - Цикл по active_discounts.
        - Умовні конструкції для перевірки знижок та захисту від від'ємної ціни.
        """
        if not self.is_available:
            raise RuntimeError(f"Страва '{self.name}' недоступна для замовлення.")

        current_price = self.price

        # 1. Спеціальна знижка на страву
        if self.special_discount_percent is not None:
            current_price -= current_price * (self.special_discount_percent / 100)

        # 2. Сезонні / накопичувальні знижки (цикл)
        if active_discounts:
            for discount in active_discounts:
                if discount.applies_to(self):
                    current_price -= current_price * (Decimal(str(discount.percent)) / 100)

        # Захист від від'ємної ціни після всіх знижок
        if current_price < 0:
            current_price = Decimal('0')

        # Округлення до 2 знаків (грошовий стандарт)
        return float(current_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    # ----------------------------------------------------------------------
    # Метод №2 (нетривіальний): Розрахунок ціни з ПДВ (умовна логіка + ставки)
    # ----------------------------------------------------------------------
    def calculate_price_with_vat(self, vat_rate: str) -> float:
        """
        Повертає ціну страви (без знижок) із доданим ПДВ.
        Підтримує ставки: 'zero', 'reduced_7', 'standard_20'.
        """
        vat_rates = {
            'zero': 1.00,
            'reduced_7': 1.07,
            'standard_20': 1.20
        }
        if vat_rate not in vat_rates:
            raise ValueError(f"Невідома ставка ПДВ: {vat_rate}. Допустимі: zero, reduced_7, standard_20")

        multiplier = Decimal(str(vat_rates[vat_rate]))
        price_with_vat = self.price * multiplier
        return float(price_with_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    # ----------------------------------------------------------------------
    # Метод №3 (нетривіальний): Комплексна валідація перед публікацією
    # ----------------------------------------------------------------------
    def validate_for_publish(self) -> ValidationResult:
        """
        Перевіряє всі поля страви: назва, ціна, знижка, URL зображення.
        Повертає ValidationResult зі списком помилок.
        """
        errors = []

        # Перевірка назви
        if not self.name or len(self.name.strip()) < 2:
            errors.append("Назва повинна містити хоча б 2 символи.")
        elif len(self.name) > 100:
            errors.append("Назва не може перевищувати 100 символів.")

        # Перевірка ціни
        if self.price < 0:
            errors.append("Ціна не може бути від'ємною.")
        elif self.price == 0:
            errors.append("Ціна не може дорівнювати нулю (безкоштовні страви не підтримуються).")
        elif self.price > 10000:
            errors.append("Ціна занадто висока (> 10000).")

        # Перевірка спеціальної знижки
        if self.special_discount_percent is not None:
            if self.special_discount_percent < 0 or self.special_discount_percent > 100:
                errors.append("Знижка має бути від 0% до 100%.")
            elif self.special_discount_percent == 100 and self.price > 0:
                errors.append("Страва не може бути повністю безкоштовною через знижку 100%.")

        # Перевірка URL зображення (якщо вказано)
        if self.image_url:
            import re
            url_pattern = re.compile(r'^https?://\S+$')
            if not url_pattern.match(self.image_url):
                errors.append("Посилання на зображення має бути коректним URL (http:// або https://).")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    # ----------------------------------------------------------------------
    # Допоміжні методи (зміна стану) – не є основними для тестування логіки
    # ----------------------------------------------------------------------
    def set_availability(self, is_available: bool) -> None:
        self.is_available = is_available

    def set_special_discount(self, discount_percent: Optional[float]) -> None:
        if discount_percent is not None and (discount_percent < 0 or discount_percent > 100):
            raise ValueError("Знижка має бути в межах 0–100.")
        self.special_discount_percent = Decimal(str(discount_percent)) if discount_percent is not None else None