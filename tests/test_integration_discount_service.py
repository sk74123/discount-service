"""
Integration test for the discount service
Tests the main scenario with PUMA T-shirt, category discount, and ICICI bank offer
"""

import asyncio
import pytest
from discount_service import DiscountService
from fake_data import cart_items_scenario_1, regular_customer, icici_card


@pytest.mark.asyncio
async def test_discount_scenario():
    """Test the main discount scenario as a high-level integration test."""
    service = DiscountService()

    # Test Case: Multiple discounts
    # Cart contains:
    # - 2x PUMA T-shirt @ ₹1000 each (base price)
    # - 1x Nike Shoes @ ₹5000
    # - 1x Adidas Jeans @ ₹2000
    # Total base price: ₹9000

    result = await service.calculate_cart_discounts(
        cart_items=cart_items_scenario_1,
        customer=regular_customer,
        payment_info=icici_card
    )

    # Assertions for expected discounts
    assert result.original_price == 9000
    assert "Min 40% off on PUMA" in result.applied_discounts
    assert "Extra 10% off on T-shirts" in result.applied_discounts
    assert "ICICI - 10% instant discount" in result.applied_discounts
    assert result.final_price < result.original_price
    assert result.message == ""

    # Test voucher code validation
    is_valid = await service.validate_discount_code("SUPER69", cart_items_scenario_1, regular_customer)
    assert is_valid is True

    is_valid = await service.validate_discount_code("VIP20", cart_items_scenario_1, regular_customer)
    assert is_valid is False

    # Test with voucher code
    result_with_voucher = await service.calculate_cart_discounts(
        cart_items=cart_items_scenario_1,
        customer=regular_customer,
        payment_info=icici_card,
        voucher_code="SUPER69"
    )
    assert result_with_voucher.final_price < result.final_price
    assert "Super Sale Voucher" in result_with_voucher.applied_discounts
    assert result_with_voucher.original_price == result.original_price
    assert result_with_voucher.final_price <= result.final_price


if __name__ == "__main__":
    asyncio.run(test_discount_scenario())