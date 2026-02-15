from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories import ProductRepository, VerificationRepository
from src.infrastructure.mysql_repository import MySQLProductRepository
from src.infrastructure.mongo_repository import MongoVerificationRepository


class UnitOfWork(ABC):
    products: ProductRepository
    verifications: VerificationRepository

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory, mongo_client, mongo_db: str):
        self._session_factory = session_factory
        self._mongo_client = mongo_client
        self._mongo_db = mongo_db
        self._session: AsyncSession = None

    async def __aenter__(self):
        self._session = self._session_factory()
        self.products = MySQLProductRepository(self._session)
        self.verifications = MongoVerificationRepository(
            self._mongo_client, self._mongo_db
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
