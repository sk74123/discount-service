"""
Unit tests for the individual discount calculation methods in DiscountService.
"""

import pytest
from decimal import Decimal
from discount_service import DiscountService
from fake_data import (
    regular_customer, icici_card, puma_tshirt, nike_shoes, adidas_jeans,
    premium_customer, upi_payment
)
from models import CartItem, Product, BrandTier


# --- Unit Tests for Individual Discount Methods ---

@pytest.fixture
def service():
    """Provides a DiscountService instance for tests."""
    return DiscountService()


def test_apply_brand_discounts(service):
    """Test the private method for applying brand discounts."""
    # Test case 1: PUMA discount (no min purchase)
    cart_puma = [CartItem(product=puma_tshirt, quantity=1, size="M")]
    discounts = service._apply_brand_discounts(cart_puma)
    assert discounts == {"Min 40% off on PUMA": Decimal('400')}

    # Test case 2: Nike discount (with min purchase met)
    cart_nike_met = [CartItem(product=nike_shoes, quantity=1, size="9")]  # 5000 > 2000
    discounts = service._apply_brand_discounts(cart_nike_met)
    assert discounts == {"30% off on Nike": Decimal('1500.0')}

    # Test case 3: Nike discount (with min purchase not met)
    cheap_nike = Product("NIKE-002", "Nike", BrandTier.REGULAR, "Socks", Decimal('1000'), Decimal('1000'))
    cart_nike_not_met = [CartItem(product=cheap_nike, quantity=1, size="L")]
    discounts = service._apply_brand_discounts(cart_nike_not_met)
    assert discounts == {}

    # Test case 4: No brand discount
    cart_adidas = [CartItem(product=adidas_jeans, quantity=1, size="32")]
    discounts = service._apply_brand_discounts(cart_adidas)
    assert discounts == {}


def test_apply_category_discounts(service):
    """Test the private method for applying category discounts."""
    # Test case 1: T-shirt discount
    cart_tshirt = [CartItem(product=puma_tshirt, quantity=1, size="M")]  # current_price=600
    discounts = service._apply_category_discounts(cart_tshirt)
    assert discounts == {"Extra 10% off on T-shirts": Decimal('60.0')}

    # Test case 2: Jeans discount (not excluded brand)
    cart_jeans = [CartItem(product=adidas_jeans, quantity=1, size="32")]  # current_price=2000
    discounts = service._apply_category_discounts(cart_jeans)
    assert discounts == {"15% off on Jeans": Decimal('300.0')}

    # Test case 3: Jeans discount (with excluded brand)
    levis_jeans = Product("LEVIS-001", "Levis", BrandTier.REGULAR, "Jeans", Decimal('3000'), Decimal('3000'))
    cart_levis = [CartItem(product=levis_jeans, quantity=1, size="32")]
    discounts = service._apply_category_discounts(cart_levis)
    assert discounts == {}


def test_apply_voucher_discount(service):
    """Test the private method for applying voucher discounts."""
    original_price = Decimal('9000')
    existing_discounts = {"Brand Discount": Decimal('1000')}

    # Test case 1: VIP voucher for non-VIP customer
    discounts = service._apply_voucher_discount("VIP20", regular_customer, original_price, existing_discounts)
    assert discounts == {}

    # Test case 2: VIP voucher for VIP customer
    discounts = service._apply_voucher_discount("VIP20", premium_customer, original_price, existing_discounts)
    subtotal = original_price - sum(existing_discounts.values())  # 8000
    expected_discount = subtotal * Decimal('0.20')  # 1600
    assert discounts == {"Voucher VIP20": expected_discount}

    # Test case 3: Voucher that hits the max discount cap
    high_price = Decimal('20000')
    discounts = service._apply_voucher_discount("SUPER69", regular_customer, high_price, {})
    # 69% of 20000 is 13800, which is > 5000 cap
    assert discounts == {"Voucher SUPER69": Decimal('5000')}


def test_apply_bank_offer(service):
    """Test the private method for applying bank offers."""
    original_price = Decimal('9000')

    # Test case 1: Valid ICICI offer
    # subtotal = 9000 - 2000 = 7000
    # 10% of 7000 is 700
    discounts = service._apply_bank_offer(icici_card, original_price, {"some": Decimal('2000')})
    assert discounts == {"ICICI - 10% instant discount": Decimal('700.0')}

    # Test case 2: ICICI offer where min purchase is not met
    discounts = service._apply_bank_offer(icici_card, Decimal('900'), {})
    assert discounts == {}

    # Test case 3: A non-card payment method
    discounts = service._apply_bank_offer(upi_payment, original_price, {})
    assert discounts == {}


def test_build_discounted_price_response(service):
    """Test the final response builder."""
    original_price = Decimal('1000')

    # Test case 1: With a set of applied discounts
    discounts = {"Discount A": Decimal('100'), "Discount B": Decimal('50.5')}
    response = service._build_discounted_price_response(original_price, discounts)

    assert response.original_price == original_price
    assert response.final_price == Decimal('849.50')
    assert "You saved ₹150.50 (15.0%)!" in response.message
    assert "Applied: Discount A: ₹100.00, Discount B: ₹50.50" in response.message

    # Test case 2: With no discounts
    response = service._build_discounted_price_response(original_price, {})
    assert response.final_price == original_price
    assert response.message == "No discounts applied"

    # Test case 3: When final price would go below zero
    response = service._build_discounted_price_response(Decimal('100'), {"Big Discount": Decimal('120')})
    assert response.final_price == Decimal('0') 