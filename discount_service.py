from decimal import Decimal
from typing import List, Optional, Dict
from models import CartItem, CustomerProfile, PaymentInfo, DiscountedPrice


# Simple configuration for discount rules
BRAND_DISCOUNTS = {
    "PUMA": {"discount": Decimal("40"), "name": "Min 40% off on PUMA"},
    "Nike": {"discount": Decimal("30"), "name": "30% off on Nike", "min_purchase": Decimal("2000")}
}

CATEGORY_DISCOUNTS = {
    "T-shirts": {"discount": Decimal("10"), "name": "Extra 10% off on T-shirts"},
    "Jeans": {"discount": Decimal("15"), "name": "15% off on Jeans", "excluded_brands": ["Levis"]}
}

BANK_OFFERS = {
    "ICICI": {"discount": Decimal("10"), "name": "ICICI - 10% instant discount", "min_purchase": Decimal("1000")},
    "HDFC": {"discount": Decimal("15"), "name": "HDFC - 15% instant discount", "min_purchase": Decimal("2000")}
}

VOUCHER_CODES = {
    "SUPER69": {"discount": Decimal("69"), "name": "Super Sale Voucher", "max_discount": Decimal("5000")},
    "VIP20": {"discount": Decimal("20"), "name": "Premium Member Voucher", "required_tier": "PREMIUM"}
}


class DiscountService:
    """
    Service for calculating discounts on shopping carts, applying brand, category, voucher, and bank offers.
    """
    async def calculate_cart_discounts(
        self,
        cart_items: List[CartItem],
        customer: CustomerProfile,
        payment_info: Optional[PaymentInfo] = None,
        voucher_code: Optional[str] = None
    ) -> DiscountedPrice:
        """
        Calculate final price after applying discount logic:
        - First apply brand/category discounts
        - Then apply coupon codes
        - Then apply bank offers
        Returns a DiscountedPrice object with details.
        """
        if not cart_items:
            return DiscountedPrice(
                original_price=Decimal('0'),
                final_price=Decimal('0'),
                applied_discounts={},
                message="Empty cart"
            )

        # Input validation: no negative prices or quantities
        for item in cart_items:
            if item.quantity < 0:
                raise ValueError("Cart item quantity cannot be negative.")
            if item.product.base_price < 0 or item.product.current_price < 0:
                raise ValueError("Product price cannot be negative.")

        original_price = sum(item.product.base_price * item.quantity for item in cart_items)
        applied_discounts = {}

        # 1. Apply brand and category discounts
        applied_discounts.update(self._apply_brand_discounts(cart_items))
        applied_discounts.update(self._apply_category_discounts(cart_items))

        # 2. Apply voucher code if provided
        if voucher_code:
            applied_discounts.update(
                self._apply_voucher_discount(voucher_code, customer, original_price, applied_discounts)
            )

        # 3. Apply bank offers
        if payment_info:
            applied_discounts.update(
                self._apply_bank_offer(payment_info, original_price, applied_discounts)
            )

        # 4. Calculate final price and generate response
        return self._build_discounted_price_response(original_price, applied_discounts)

    def _apply_brand_discounts(self, cart_items: List[CartItem]) -> Dict[str, Decimal]:
        """
        Applies discounts based on product brand.
        Returns a dictionary of discount names to amounts.
        """
        brand_discounts = {}
        for item in cart_items:
            if item.product.brand in BRAND_DISCOUNTS:
                brand_rule = BRAND_DISCOUNTS[item.product.brand]

                # Check minimum purchase for brand
                if "min_purchase" in brand_rule:
                    brand_total = sum(
                        ci.product.base_price * ci.quantity
                        for ci in cart_items
                        if ci.product.brand == item.product.brand
                    )
                    if brand_total < brand_rule["min_purchase"]:
                        continue

                discount_amount = item.product.base_price * item.quantity * brand_rule["discount"] / 100
                discount_name = brand_rule["name"]
                brand_discounts[discount_name] = brand_discounts.get(discount_name, Decimal('0')) + discount_amount
        return brand_discounts

    def _apply_category_discounts(self, cart_items: List[CartItem]) -> Dict[str, Decimal]:
        """
        Applies discounts based on product category.
        Returns a dictionary of discount names to amounts.
        """
        category_discounts = {}
        for item in cart_items:
            if item.product.category in CATEGORY_DISCOUNTS:
                category_rule = CATEGORY_DISCOUNTS[item.product.category]

                # Check brand exclusions
                if "excluded_brands" in category_rule and item.product.brand in category_rule["excluded_brands"]:
                    continue

                discount_amount = item.product.current_price * item.quantity * category_rule["discount"] / 100
                discount_name = category_rule["name"]
                category_discounts[discount_name] = category_discounts.get(discount_name, Decimal('0')) + discount_amount
        return category_discounts

    def _apply_voucher_discount(self, voucher_code: str, customer: CustomerProfile, original_price: Decimal, existing_discounts: Dict[str, Decimal]) -> Dict[str, Decimal]:
        """
        Applies a voucher code discount if valid.
        Returns a dictionary of discount names to amounts.
        """
        voucher_discounts = {}
        if voucher_code in VOUCHER_CODES:
            voucher_rule = VOUCHER_CODES[voucher_code]

            # Check customer tier requirement
            if "required_tier" in voucher_rule and customer.tier != voucher_rule["required_tier"]:
                return voucher_discounts  # Skip this voucher

            # Calculate discount on total after brand/category discounts
            total_after_discounts = original_price - sum(existing_discounts.values())
            voucher_discount = total_after_discounts * voucher_rule["discount"] / 100

            # Apply max discount cap
            if "max_discount" in voucher_rule and voucher_discount > voucher_rule["max_discount"]:
                voucher_discount = voucher_rule["max_discount"]

            voucher_discounts[f"Voucher {voucher_code}"] = voucher_discount
        return voucher_discounts

    def _apply_bank_offer(self, payment_info: PaymentInfo, original_price: Decimal, existing_discounts: Dict[str, Decimal]) -> Dict[str, Decimal]:
        """
        Applies bank offers if applicable.
        Returns a dictionary of discount names to amounts.
        """
        bank_discounts = {}
        if payment_info.method == "CARD" and payment_info.bank_name in BANK_OFFERS:
            bank_rule = BANK_OFFERS[payment_info.bank_name]

            # Check minimum purchase
            if "min_purchase" in bank_rule and original_price < bank_rule["min_purchase"]:
                return bank_discounts  # Skip bank discount

            # Calculate discount on total after all other discounts
            total_after_discounts = original_price - sum(existing_discounts.values())
            bank_discount = total_after_discounts * bank_rule["discount"] / 100

            bank_discounts[bank_rule["name"]] = bank_discount
        return bank_discounts

    def _build_discounted_price_response(self, original_price: Decimal, applied_discounts: Dict[str, Decimal]) -> DiscountedPrice:
        """
        Calculates the final price and constructs the response object.
        """
        total_discount = sum(applied_discounts.values())
        final_price = original_price - total_discount

        # Ensure final price is not negative
        if final_price < 0:
            final_price = Decimal('0')

        # Generate message with more detail
        messages = []
        if applied_discounts:
            savings_percent = (total_discount / original_price * 100) if original_price > 0 else 0
            messages.append(f"You saved ₹{total_discount:.2f} ({savings_percent:.1f}%)!")
            messages.append("Applied: " + ", ".join(
                f"{name}: ₹{amount:.2f}" for name, amount in applied_discounts.items()
            ))
        else:
            messages.append("No discounts applied")

        message = " ".join(messages)

        return DiscountedPrice(
            original_price=original_price,
            final_price=final_price.quantize(Decimal('0.01')),
            applied_discounts=applied_discounts,
            message=message
        )
    
    async def validate_discount_code(
        self,
        code: str,
        cart_items: List[CartItem],
        customer: CustomerProfile
    ) -> bool:
        """
        Validate if a discount code can be applied for the given cart and customer.
        Returns True if valid, False otherwise.
        """
        if code not in VOUCHER_CODES:
            return False
        
        voucher_rule = VOUCHER_CODES[code]
        
        # Check customer tier requirement
        if "required_tier" in voucher_rule and customer.tier != voucher_rule["required_tier"]:
            return False
        
        # For simplicity, return True if code exists and tier matches
        return True