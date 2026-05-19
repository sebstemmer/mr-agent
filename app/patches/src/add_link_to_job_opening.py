from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.patcher.src.patch import Patch


class AddLinkToJobOpening(Patch):
    version = 3

    async def apply(self, session: AsyncSession) -> None:
        await session.exec(
            text("ALTER TABLE job_opening ADD COLUMN IF NOT EXISTS link_to_job_opening VARCHAR")
        )
        await session.commit()
