from sqlalchemy.ext.asyncio import async_sessionmaker

from job_search.src.job_opening_model import JobOpening


class JobOpeningRepository:
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def save(self, job_opening: JobOpening) -> JobOpening:
        async with self._session_factory() as session:
            session.add(job_opening)
            await session.commit()
            await session.refresh(job_opening)
            return job_opening
