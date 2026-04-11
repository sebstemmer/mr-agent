from datetime import date

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import select, update

from job_search.src.job_model import Job


class JobRepository:
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def find_by_job_id(self, job_id: str) -> Job | None:
        async with self._session_factory() as session:
            result = await session.exec(select(Job).where(Job.job_id == job_id))
            return result.first()

    async def exists_by_id(self, job_id: str) -> bool:
        result = await self.find_by_job_id(job_id=job_id)
        return result is not None

    async def find_all_interesting(self) -> list[Job]:
        async with self._session_factory() as session:
            result = await session.exec(
                select(Job).where(Job.of_interest == True, Job.link != None)
            )
            return list(result.all())

    async def find_by_of_interest_and_link_not_null_and_created_at_between(
        self, of_interest: bool, start_date: date, end_date: date
    ) -> list[Job]:
        async with self._session_factory() as session:
            result = await session.exec(
                select(Job).where(
                    Job.of_interest == of_interest,
                    Job.link != None,
                    Job.created_at >= start_date,
                    Job.created_at <= end_date,
                )
            )
            return list(result.all())

    async def save(self, job: Job) -> Job:
        async with self._session_factory() as session:
            session.add(job)
            await session.commit()
            await session.refresh(job)
            return job

    async def update_liked_by_user_by_public_id(
        self, public_id: str, liked_by_user: bool
    ) -> bool:
        async with self._session_factory() as session:
            result = await session.exec(
                update(Job)
                .where(Job.public_id == public_id)
                .values(liked_by_user=liked_by_user)
            )
            await session.commit()
            return result.rowcount > 0
