from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domain import Product, ProductStatus
from src.domain.repositories import ProductRepository
from src.infrastructure.mysql_models import ProductModel


class MySQLProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, product: Product) -> None:
        model = ProductModel(
            id=product.product_id,
            name=product.name,
            price=product.price,
            currency=product.currency,
            category=product.category,
            stock_quantity=product.stock_quantity,
            assets=product.assets,
            status=product.status.value,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )
        self._session.add(model)
        await self._session.flush()

    async def find_by_id(self, product_id: str) -> Optional[Product]:
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return Product(
            product_id=model.id,
            name=model.name,
            price=model.price,
            currency=model.currency,
            category=model.category,
            stock_quantity=model.stock_quantity,
            assets=model.assets,
            status=ProductStatus(model.status.value),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def update(self, product: Product) -> None:
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id == product.product_id)
        )
        model = result.scalar_one_or_none()

        if model:
            model.name = product.name
            model.price = product.price
            model.currency = product.currency
            model.category = product.category
            model.stock_quantity = product.stock_quantity
            model.assets = product.assets
            model.status = product.status.value
            model.updated_at = product.updated_at
            await self._session.flush()
