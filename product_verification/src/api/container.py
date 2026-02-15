from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient

from src.infrastructure import SQLAlchemyUnitOfWork
from src.domain.event_dispatcher import InMemoryEventDispatcher
from src.use_cases import CreateProductUseCase, VerifyProductUseCase, GetProductUseCase


class Container:
    def __init__(self, mysql_url: str, mongo_url: str, mongo_db: str):
        self._mysql_engine = create_async_engine(mysql_url, echo=False)
        self._session_factory = async_sessionmaker(
            self._mysql_engine, class_=AsyncSession, expire_on_commit=False
        )
        self._mongo_client = AsyncIOMotorClient(mongo_url)
        self._mongo_db = mongo_db
        self._event_dispatcher = InMemoryEventDispatcher()

    def get_uow(self) -> SQLAlchemyUnitOfWork:
        return SQLAlchemyUnitOfWork(
            self._session_factory, self._mongo_client, self._mongo_db
        )

    def get_event_dispatcher(self) -> InMemoryEventDispatcher:
        return self._event_dispatcher

    def get_create_product_use_case(self) -> CreateProductUseCase:
        return CreateProductUseCase(self.get_uow(), self.get_event_dispatcher())

    def get_verify_product_use_case(self) -> VerifyProductUseCase:
        return VerifyProductUseCase(self.get_uow(), self.get_event_dispatcher())

    def get_get_product_use_case(self) -> GetProductUseCase:
        return GetProductUseCase(self.get_uow())

    async def close(self):
        await self._mysql_engine.dispose()
        self._mongo_client.close()
