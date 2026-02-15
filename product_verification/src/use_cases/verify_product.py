from src.infrastructure.unit_of_work import UnitOfWork
from src.application import ProductService
from src.domain import Product, ProductVerificationPolicy
from src.domain.event_dispatcher import EventDispatcher


class VerifyProductUseCase:
    def __init__(self, uow: UnitOfWork, event_dispatcher: EventDispatcher):
        self._uow = uow
        self._event_dispatcher = event_dispatcher

    async def execute(self, product_id: str) -> Product:
        async with self._uow:
            verification_policy = ProductVerificationPolicy()
            service = ProductService(
                self._uow.products, self._uow.verifications, verification_policy
            )

            product = await service.get_product(product_id)

            await service.verify_product(product)

            await self._uow.commit()

            await self._event_dispatcher.dispatch_all(product.get_domain_events())
            product.clear_domain_events()

            return product
