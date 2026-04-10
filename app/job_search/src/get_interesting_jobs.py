from datetime import date

from job_search.src.job_model import Job
from job_search.src.job_repository import JobRepository


class GetInterestingJobs:
    def __init__(self, job_repo: JobRepository):
        self._job_repo = job_repo

    async def get(self, start_date: date, end_date: date) -> list[Job]:
        return await self._job_repo.find_by_of_interest_and_link_not_null_and_created_at_between(
            of_interest=True,
            start_date=start_date,
            end_date=end_date,
        )
