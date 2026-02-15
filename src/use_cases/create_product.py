from typing import List

from src.infrastructure.unit_of_work import UnitOfWork
from src.application import ProductService
from src.domain import Product, ProductVerificationPolicy
from src.domain.event_dispatcher import EventDispatcher


class CreateProductUseCase:
    def __init__(self, uow: UnitOfWork, event_dispatcher: EventDispatcher):
        self._uow = uow
        self._event_dispatcher = event_dispatcher

    async def execute(
        self,
        name: str,
        price: float,
        currency: str,
        category: str,
        stock_quantity: int,
        assets: List[str],
    ) -> Product:
        async with self._uow:
            verification_policy = ProductVerificationPolicy()
            service = ProductService(
                self._uow.products, self._uow.verifications, verification_policy
            )

            product = await service.create_product(
                name=name,
                price=price,
                currency=currency,
                category=category,
                stock_quantity=stock_quantity,
                assets=assets,
            )

            await self._uow.commit()

            await self._event_dispatcher.dispatch_all(product.get_domain_events())
            product.clear_domain_events()

            return product
