from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from src.domain import Product


class ProductRepository(ABC):
    @abstractmethod
    async def save(self, product: Product) -> None:
        pass

    @abstractmethod
    async def find_by_id(self, product_id: str) -> Optional[Product]:
        pass

    @abstractmethod
    async def update(self, product: Product) -> None:
        pass


class VerificationRepository(ABC):
    @abstractmethod
    async def save_verification(
        self,
        product_id: str,
        checks: dict,
        reasons: List[str],
        verified_at: datetime,
    ) -> None:
        pass

    @abstractmethod
    async def find_by_product_id(self, product_id: str) -> Optional[dict]:
        pass
