from typing import List
from datetime import datetime
from uuid import uuid4

from src.domain import (
    Product,
    ProductStatus,
    ProductCreatedPendingVerification,
    ProductVerificationCompleted,
)
from src.domain.verification_policy import ProductVerificationPolicy
from src.domain.repositories import ProductRepository, VerificationRepository


class ProductService:
    def __init__(
        self,
        product_repository: ProductRepository,
        verification_repository: VerificationRepository,
        verification_policy: ProductVerificationPolicy,
    ):
        self._product_repository = product_repository
        self._verification_repository = verification_repository
        self._verification_policy = verification_policy

    async def create_product(
        self,
        name: str,
        price: float,
        currency: str,
        category: str,
        stock_quantity: int,
        assets: List[str],
    ) -> Product:
        product_id = str(uuid4())

        product = Product(
            product_id=product_id,
            name=name,
            price=price,
            currency=currency,
            category=category,
            stock_quantity=stock_quantity,
            assets=assets,
            status=ProductStatus.PENDING_VERIFICATION,
        )

        event = ProductCreatedPendingVerification(
            product_id=product.product_id,
            name=product.name,
            price=product.price,
            currency=product.currency,
        )
        product.add_domain_event(event)

        await self._product_repository.save(product)

        return product

    async def verify_product(self, product: Product) -> None:
        verification_result = self._verification_policy.evaluate(
            name=product.name,
            category=product.category,
            currency=product.currency,
            price=product.price,
            stock_quantity=product.stock_quantity,
            assets=product.assets,
        )

        checks = {
            "name_present": bool(product.name and product.name.strip()),
            "category_present": bool(product.category and product.category.strip()),
            "currency_present": bool(product.currency and product.currency.strip()),
            "price_valid": product.price > 0,
            "stock_quantity_valid": product.stock_quantity >= 0,
            "assets_present": len(product.assets) > 0,
        }

        if verification_result.passed:
            product.transition_to_active()
        else:
            product.transition_to_rejected()

        await self._verification_repository.save_verification(
            product_id=product.product_id,
            checks=checks,
            reasons=verification_result.reasons,
            verified_at=datetime.utcnow(),
        )

        await self._product_repository.update(product)

        event = ProductVerificationCompleted(
            product_id=product.product_id,
            status=product.status,
            reasons=verification_result.reasons,
        )
        product.add_domain_event(event)

    async def get_product(self, product_id: str) -> Product:
        product = await self._product_repository.find_by_id(product_id)
        if product is None:
            raise ValueError(f"Product {product_id} not found")
        return product
