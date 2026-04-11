from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.patcher.src.patch import Patch


class AddLikedByUserToJob(Patch):
    version = 1

    async def apply(self, session: AsyncSession) -> None:
        await session.exec(
            text("ALTER TABLE job ADD COLUMN IF NOT EXISTS liked_by_user BOOLEAN")
        )
        await session.commit()
