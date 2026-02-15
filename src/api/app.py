from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api.router import router
from src.api.container import Container
from src.infrastructure.mysql_models import Base

container = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global container

    mysql_url = "mysql+aiomysql://root:password@localhost:3306/product_db"
    mongo_url = "mongodb://localhost:27017"
    mongo_db = "product_verification"

    container = Container(mysql_url, mongo_url, mongo_db)

    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(mysql_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await container.close()


app = FastAPI(title="Product Verification API", lifespan=lifespan)

app.include_router(router)
