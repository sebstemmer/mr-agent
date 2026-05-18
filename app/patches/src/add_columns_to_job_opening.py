from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.patcher.src.patch import Patch


class AddColumnsToJobOpening(Patch):
    version = 2

    async def apply(self, session: AsyncSession) -> None:
        await session.exec(
            text("ALTER TABLE job_opening ADD COLUMN IF NOT EXISTS uuid VARCHAR NOT NULL DEFAULT ''")
        )
        await session.exec(
            text("ALTER TABLE job_opening ADD COLUMN IF NOT EXISTS requirements TEXT NOT NULL DEFAULT ''")
        )
        await session.exec(
            text("ALTER TABLE job_opening ADD COLUMN IF NOT EXISTS rating INTEGER NOT NULL DEFAULT 0")
        )
        await session.exec(
            text("ALTER TABLE job_opening ADD COLUMN IF NOT EXISTS rating_reason TEXT NOT NULL DEFAULT ''")
        )
        await session.exec(
            text("ALTER TABLE job_opening ADD COLUMN IF NOT EXISTS applied BOOLEAN NOT NULL DEFAULT FALSE")
        )
        await session.exec(
            text("ALTER TABLE job_opening ADD COLUMN IF NOT EXISTS applied_at DATE")
        )
        await session.exec(
            text("ALTER TABLE job_opening ADD COLUMN IF NOT EXISTS asked_salary VARCHAR")
        )
        await session.exec(
            text("ALTER TABLE job_opening ADD COLUMN IF NOT EXISTS application_file_uuid VARCHAR")
        )
        await session.exec(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ix_job_opening_uuid ON job_opening (uuid)")
        )
        await session.commit()
