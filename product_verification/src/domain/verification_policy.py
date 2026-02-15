from dataclasses import dataclass
from typing import List


@dataclass
class VerificationResult:
    passed: bool
    reasons: List[str]


class ProductVerificationPolicy:
    def evaluate(
        self,
        name: str,
        category: str,
        currency: str,
        price: float,
        stock_quantity: int,
        assets: List[str],
    ) -> VerificationResult:
        reasons = []

        if not name or not name.strip():
            reasons.append("name is missing or empty")

        if not category or not category.strip():
            reasons.append("category is missing or empty")

        if not currency or not currency.strip():
            reasons.append("currency is missing or empty")

        if price <= 0:
            reasons.append("price must be greater than 0")

        if stock_quantity < 0:
            reasons.append("stock_quantity must be >= 0")

        if not assets or len(assets) == 0:
            reasons.append("at least 1 asset is required")

        passed = len(reasons) == 0
        return VerificationResult(passed=passed, reasons=reasons)
