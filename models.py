from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime
from decimal import Decimal
from enum import Enum


class BrandTier(Enum):
    """Enumeration for product brand tiers."""
    PREMIUM = "premium"
    REGULAR = "regular"
    BUDGET = "budget"


@dataclass
class Product:
    """Represents a product in the catalog."""
    id: str
    brand: str
    brand_tier: BrandTier
    category: str
    base_price: Decimal
    current_price: Decimal  # After brand/category discount

    def __post_init__(self):
        if self.base_price < 0:
            raise ValueError("Product base_price cannot be negative.")
        if self.current_price < 0:
            raise ValueError("Product current_price cannot be negative.")


@dataclass
class CartItem:
    """Represents an item in the shopping cart."""
    product: Product
    quantity: int
    size: str

    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError("CartItem quantity cannot be negative.")


@dataclass
class PaymentInfo:
    """Represents payment method and bank/card details."""
    method: str  # CARD, UPI, etc
    bank_name: Optional[str]
    card_type: Optional[str]  # CREDIT, DEBIT


@dataclass
class CustomerProfile:
    """Represents a customer profile."""
    id: str
    tier: str  # PREMIUM, GOLD, SILVER, etc
    member_since: datetime
    total_purchases: Decimal


@dataclass
class DiscountedPrice:
    """Represents the result of a discount calculation."""
    original_price: Decimal
    final_price: Decimal
    applied_discounts: Dict[str, Decimal]  # discount_name -> amount
    message: str