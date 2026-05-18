from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from job_search.src.job_opening_model import JobOpening


class JobOpeningRepository:
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def save(self, job_opening: JobOpening) -> JobOpening:
        async with self._session_factory() as session:
            merged = await session.merge(job_opening)
            await session.commit()
            await session.refresh(merged)
            return merged

    async def find_by_uuid(self, uuid: str) -> JobOpening | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(JobOpening).where(JobOpening.uuid == uuid)
            )
            return result.scalar_one_or_none()

    async def find_all(self) -> list[JobOpening]:
        async with self._session_factory() as session:
            result = await session.execute(select(JobOpening))
            return list(result.scalars().all())

    async def delete_by_uuid(self, uuid: str) -> None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(JobOpening).where(JobOpening.uuid == uuid)
            )
            job_opening = result.scalar_one_or_none()
            if job_opening is None:
                raise ValueError(f"Job opening not found: {uuid}")
            await session.delete(job_opening)
            await session.commit()
