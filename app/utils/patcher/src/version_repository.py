from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import select

from utils.patcher.src.version_model import Version


class VersionRepository:
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def find(self) -> Version | None:
        async with self._session_factory() as session:
            result = await session.exec(select(Version))
            return result.first()

    async def save(self, version: Version) -> Version:
        async with self._session_factory() as session:
            session.add(version)
            await session.commit()
            await session.refresh(version)
            return version
