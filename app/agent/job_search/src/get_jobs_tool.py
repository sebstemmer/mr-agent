from datetime import date
from typing import Type

from job_search.src.job_repository import JobRepository
from job_search.src.refresh_jobs import RefreshJobs
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from utils.src.sync_run_not_implemented import SyncRunNotImplemented

from agent.job_search.src.format_jobs import format_jobs


class GetJobsInput(BaseModel):
    start_date: str = Field(description="Start date in YYYY-MM-DD format (inclusive)")
    end_date: str = Field(description="End date in YYYY-MM-DD format (inclusive)")


class GetJobsTool(BaseTool):
    name: str = "get_jobs"
    description: str = "Returns job postings for a given date range."
    args_schema: Type[BaseModel] = GetJobsInput
    job_repo: JobRepository
    refresh_jobs: RefreshJobs

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, start_date: str, end_date: str) -> str:
        await self.refresh_jobs.refresh()

        jobs = await self.job_repo.find_by_of_interest_and_link_not_null_and_created_at_between(
            of_interest=True,
            start_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date),
        )

        return format_jobs(jobs=jobs)

    def _run(self, start_date: str, end_date: str) -> str:
        raise SyncRunNotImplemented()
