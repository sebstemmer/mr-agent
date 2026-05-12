import json
from datetime import date
from typing import Type

from job_search.src.get_interesting_jobs import GetInterestingJobs
from job_search.src.refresh_jobs import RefreshJobs
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

from agent.job_search.src.format_jobs import format_jobs

TOOL_NAME = "get_jobs"


class GetJobsInput(BaseModel):
    start_date: str = Field(description="Start date in YYYY-MM-DD format (inclusive).")
    end_date: str = Field(description="End date in YYYY-MM-DD format (inclusive).")


class GetJobsTool(BaseTool):
    name: str = TOOL_NAME
    description: str = "Returns job postings for a given date range."
    args_schema: Type[BaseModel] = GetJobsInput
    response_format: str = "content_and_artifact"
    get_interesting_jobs: GetInterestingJobs
    refresh_jobs: RefreshJobs

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, start_date: str, end_date: str) -> tuple[str, str]:
        await self.refresh_jobs.refresh()

        jobs = await self.get_interesting_jobs.get(
            start_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date),
        )

        if not jobs:
            return "No interesting jobs found.", "No interesting jobs found."

        context = json.dumps(
            [
                {
                    "index": index,
                    "public_id": job.public_id,
                    "title": job.summary,
                }
                for index, job in enumerate(jobs, start=1)
            ]
        )
        user_content = format_jobs(jobs=jobs)
        return context, user_content

    def _run(self, **_kwargs) -> str:
        raise SyncRunNotImplemented()
