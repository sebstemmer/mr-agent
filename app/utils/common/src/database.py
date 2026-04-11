from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def create_engine(user: str, password: str, host: str, db: str) -> AsyncEngine:
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=user,
        password=password,
        host=host,
        port=5432,
        database=db,
    )
    return create_async_engine(url)
