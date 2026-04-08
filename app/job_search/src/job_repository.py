from datetime import date

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from job_search.src.job_model import Job


class JobRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_job_id(self, job_id: str) -> Job | None:
        result = await self._session.exec(select(Job).where(Job.job_id == job_id))
        return result.first()

    async def exists_by_id(self, job_id: str) -> bool:
        result = await self.find_by_job_id(job_id=job_id)
        return result is not None

    async def find_all_interesting(self) -> list[Job]:
        result = await self._session.exec(
            select(Job).where(Job.of_interest == True, Job.link != None)
        )
        return list(result.all())

    async def find_by_of_interest_and_created_at(
        self, of_interest: bool, created_at: date
    ) -> list[Job]:
        result = await self._session.exec(
            select(Job).where(
                Job.of_interest == of_interest,
                Job.created_at == created_at,
            )
        )
        return list(result.all())

    async def find_by_of_interest_and_link_not_null_and_created_at_between(
        self, of_interest: bool, start_date: date, end_date: date
    ) -> list[Job]:
        result = await self._session.exec(
            select(Job).where(
                Job.of_interest == of_interest,
                Job.link != None,
                Job.created_at >= start_date,
                Job.created_at <= end_date,
            )
        )
        return list(result.all())

    async def save(self, job: Job) -> Job:
        self._session.add(job)
        await self._session.commit()
        await self._session.refresh(job)
        return job
