import pytest
from src.domain.verification_policy import ProductVerificationPolicy


class TestProductVerificationPolicy:
    def setup_method(self):
        self.policy = ProductVerificationPolicy()

    def test_all_checks_pass(self):
        result = self.policy.evaluate(
            name="Test Product",
            category="Electronics",
            currency="USD",
            price=99.99,
            stock_quantity=10,
            assets=["image1.jpg"],
        )

        assert result.passed is True
        assert len(result.reasons) == 0

    def test_missing_name(self):
        result = self.policy.evaluate(
            name="",
            category="Electronics",
            currency="USD",
            price=99.99,
            stock_quantity=10,
            assets=["image1.jpg"],
        )

        assert result.passed is False
        assert "name is missing or empty" in result.reasons

    def test_missing_category(self):
        result = self.policy.evaluate(
            name="Test Product",
            category="",
            currency="USD",
            price=99.99,
            stock_quantity=10,
            assets=["image1.jpg"],
        )

        assert result.passed is False
        assert "category is missing or empty" in result.reasons

    def test_missing_currency(self):
        result = self.policy.evaluate(
            name="Test Product",
            category="Electronics",
            currency="",
            price=99.99,
            stock_quantity=10,
            assets=["image1.jpg"],
        )

        assert result.passed is False
        assert "currency is missing or empty" in result.reasons

    def test_invalid_price_zero(self):
        result = self.policy.evaluate(
            name="Test Product",
            category="Electronics",
            currency="USD",
            price=0,
            stock_quantity=10,
            assets=["image1.jpg"],
        )

        assert result.passed is False
        assert "price must be greater than 0" in result.reasons

    def test_invalid_price_negative(self):
        result = self.policy.evaluate(
            name="Test Product",
            category="Electronics",
            currency="USD",
            price=-10,
            stock_quantity=10,
            assets=["image1.jpg"],
        )

        assert result.passed is False
        assert "price must be greater than 0" in result.reasons

    def test_negative_stock_quantity(self):
        result = self.policy.evaluate(
            name="Test Product",
            category="Electronics",
            currency="USD",
            price=99.99,
            stock_quantity=-1,
            assets=["image1.jpg"],
        )

        assert result.passed is False
        assert "stock_quantity must be >= 0" in result.reasons

    def test_zero_stock_quantity_passes(self):
        result = self.policy.evaluate(
            name="Test Product",
            category="Electronics",
            currency="USD",
            price=99.99,
            stock_quantity=0,
            assets=["image1.jpg"],
        )

        assert result.passed is True

    def test_no_assets(self):
        result = self.policy.evaluate(
            name="Test Product",
            category="Electronics",
            currency="USD",
            price=99.99,
            stock_quantity=10,
            assets=[],
        )

        assert result.passed is False
        assert "at least 1 asset is required" in result.reasons

    def test_multiple_failures(self):
        result = self.policy.evaluate(
            name="",
            category="",
            currency="",
            price=-10,
            stock_quantity=-5,
            assets=[],
        )

        assert result.passed is False
        assert len(result.reasons) == 6
        assert "name is missing or empty" in result.reasons
        assert "category is missing or empty" in result.reasons
        assert "currency is missing or empty" in result.reasons
        assert "price must be greater than 0" in result.reasons
        assert "stock_quantity must be >= 0" in result.reasons
        assert "at least 1 asset is required" in result.reasons
