from src.infrastructure.unit_of_work import UnitOfWork
from src.application import ProductService
from src.domain import Product, ProductVerificationPolicy


class GetProductUseCase:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, product_id: str) -> Product:
        async with self._uow:
            verification_policy = ProductVerificationPolicy()
            service = ProductService(
                self._uow.products, self._uow.verifications, verification_policy
            )

            product = await service.get_product(product_id)

            return product
