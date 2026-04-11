from abc import ABC, abstractmethod

from sqlmodel.ext.asyncio.session import AsyncSession


class Patch(ABC):
    version: int

    @abstractmethod
    async def apply(self, session: AsyncSession) -> None: ...
