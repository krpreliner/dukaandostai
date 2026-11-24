from typing import Dict, Any, Tuple

class ProfitCalculator:
    """
    Deterministic Python financial validation and calculation engine.
    Never relies on LLM approximations. Enforces business guardrails.
    """
    @staticmethod
    def calculate_unit_margin(cost_price: float, selling_price: float) -> Tuple[float, float]:
        """
        Returns (unit_profit, margin_percentage)
        """
        unit_profit = round(selling_price - cost_price, 2)
        if selling_price <= 0:
            return unit_profit, -100.0
        margin_pct = round((unit_profit / selling_price) * 100.0, 2)
        return unit_profit, margin_pct

    @staticmethod
    def validate_pricing(
        cost_price: float,
        proposed_price: float,
        original_price: float,
        max_discount_pct: float = 15.0
    ) -> Dict[str, Any]:
        """
        Validates if proposed price meets business rules:
        1. Non-negative gross profit (selling_price > cost_price).
        2. Discount does not exceed max_discount_pct.
        """
        unit_profit, margin_pct = ProfitCalculator.calculate_unit_margin(cost_price, proposed_price)
        
        # Calculate discount percentage
        discount_amount = max(0.0, round(original_price - proposed_price, 2))
        discount_pct = round((discount_amount / original_price) * 100.0, 2) if original_price > 0 else 0.0

        is_valid = True
        reasons = []

        if proposed_price <= cost_price:
            is_valid = False
            reasons.append(
                f"Negative gross margin! Proposed price ₹{proposed_price:.2f} is at or below cost price ₹{cost_price:.2f} (Loss / Non-positive: ₹{unit_profit:.2f}/unit)."
            )

        if discount_pct > max_discount_pct:
            is_valid = False
            reasons.append(
                f"Discount {discount_pct:.1f}% exceeds business policy maximum of {max_discount_pct:.1f}%."
            )

        return {
            "is_valid": is_valid,
            "cost_price": cost_price,
            "original_price": original_price,
            "proposed_price": proposed_price,
            "unit_profit": unit_profit,
            "gross_margin_pct": margin_pct,
            "discount_pct": discount_pct,
            "reasons": reasons
        }

    @staticmethod
    def calculate_campaign_impact(
        cost_price: float,
        promo_price: float,
        projected_units: int,
        fixed_marketing_cost: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculates projected incremental gross and net profit.
        """
        unit_profit, margin_pct = ProfitCalculator.calculate_unit_margin(cost_price, promo_price)
        gross_profit = round(unit_profit * projected_units, 2)
        net_profit = round(gross_profit - fixed_marketing_cost, 2)
        return {
            "unit_profit": unit_profit,
            "gross_margin_pct": margin_pct,
            "projected_units": projected_units,
            "gross_profit": gross_profit,
            "fixed_cost": fixed_marketing_cost,
            "net_profit": net_profit
        }
