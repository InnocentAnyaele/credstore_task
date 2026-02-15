from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from src.domain.repositories import VerificationRepository


class MongoVerificationRepository(VerificationRepository):
    def __init__(self, client: AsyncIOMotorClient, database: str):
        self._db = client[database]
        self._collection = self._db["verifications"]

    async def save_verification(
        self,
        product_id: str,
        checks: dict,
        reasons: List[str],
        verified_at: datetime,
    ) -> None:
        document = {
            "product_id": product_id,
            "checks": checks,
            "reasons": reasons,
            "verified_at": verified_at,
        }
        await self._collection.insert_one(document)

    async def find_by_product_id(self, product_id: str) -> Optional[dict]:
        document = await self._collection.find_one({"product_id": product_id})
        if document:
            document.pop("_id", None)
        return document
