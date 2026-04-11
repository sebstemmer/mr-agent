from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from utils.patcher.src.version_model import Version


class VersionRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find(self) -> Version | None:
        result = await self._session.exec(select(Version))
        return result.first()

    async def save(self, version: Version) -> Version:
        self._session.add(version)
        await self._session.commit()
        await self._session.refresh(version)
        return version
