import secrets
import string

from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.patcher.src.patch import Patch

_PUBLIC_ID_ALPHABET = string.ascii_lowercase + string.digits
_PUBLIC_ID_LENGTH = 5


def _generate_public_id() -> str:
    return "".join(
        secrets.choice(_PUBLIC_ID_ALPHABET) for _ in range(_PUBLIC_ID_LENGTH)
    )


class AddPublicIdToJob(Patch):
    version = 0

    async def apply(self, session: AsyncSession) -> None:
        await session.exec(
            text("ALTER TABLE job ADD COLUMN IF NOT EXISTS public_id VARCHAR")
        )

        result = await session.exec(
            text("SELECT id FROM job WHERE public_id IS NULL")
        )
        job_ids = [row[0] for row in result.all()]

        used: set[str] = set()
        for job_id in job_ids:
            while True:
                public_id = _generate_public_id()
                if public_id not in used:
                    used.add(public_id)
                    break
            await session.exec(
                text("UPDATE job SET public_id = :public_id WHERE id = :id").bindparams(
                    public_id=public_id, id=job_id
                )
            )

        await session.exec(
            text("ALTER TABLE job ALTER COLUMN public_id SET NOT NULL")
        )
        await session.exec(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_job_public_id ON job (public_id)"
            )
        )
        await session.commit()
