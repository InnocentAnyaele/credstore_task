from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api.router import router
from src.api.container import Container
from src.infrastructure.mysql_models import Base
from sqlalchemy.pool import NullPool

MYSQL_URL = "mysql+aiomysql://root:password@localhost:3306/product_db"
MONGO_URL = "mongodb://localhost:27017"
MONGO_DB = "product_verification"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.container = Container(MYSQL_URL, MONGO_URL, MONGO_DB)

    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(MYSQL_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await app.state.container.close()


app = FastAPI(title="Product Verification API", lifespan=lifespan)

app.include_router(router)
