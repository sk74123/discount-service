"""
Fake data for testing the discount service
Scenario: 
- PUMA T-shirt with "Min 40% off"
- Additional 10% off on T-shirts category
- ICICI bank offer of 10% instant discount
"""

from datetime import datetime
from decimal import Decimal
from discount_service.models import Product, CartItem, CustomerProfile, PaymentInfo, BrandTier


# Products
puma_tshirt = Product(
    id="PUMA-001",
    brand="PUMA",
    brand_tier=BrandTier.REGULAR,
    category="T-shirts",
    base_price=Decimal('1000'),
    current_price=Decimal('600')  # After 40% brand discount
)

nike_shoes = Product(
    id="NIKE-001",
    brand="Nike",
    brand_tier=BrandTier.PREMIUM,
    category="Shoes",
    base_price=Decimal('5000'),
    current_price=Decimal('5000')  # No brand discount yet
)

adidas_jeans = Product(
    id="ADIDAS-001",
    brand="Adidas",
    brand_tier=BrandTier.REGULAR,
    category="Jeans",
    base_price=Decimal('2000'),
    current_price=Decimal('2000')  # No brand discount
)

# Cart Items
cart_items_scenario_1 = [
    CartItem(product=puma_tshirt, quantity=2, size="M"),
    CartItem(product=nike_shoes, quantity=1, size="9"),
    CartItem(product=adidas_jeans, quantity=1, size="32")
]

cart_items_only_puma = [
    CartItem(product=puma_tshirt, quantity=3, size="L")
]

# Customers
premium_customer = CustomerProfile(
    id="CUST-001",
    tier="PREMIUM",
    member_since=datetime(2020, 1, 1),
    total_purchases=Decimal('50000')
)

regular_customer = CustomerProfile(
    id="CUST-002",
    tier="SILVER",
    member_since=datetime(2023, 1, 1),
    total_purchases=Decimal('5000')
)

# Payment Methods
icici_card = PaymentInfo(
    method="CARD",
    bank_name="ICICI",
    card_type="CREDIT"
)

hdfc_card = PaymentInfo(
    method="CARD",
    bank_name="HDFC",
    card_type="DEBIT"
)

upi_payment = PaymentInfo(
    method="UPI",
    bank_name=None,
    card_type=None
)