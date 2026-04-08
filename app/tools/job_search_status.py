from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from job_search.src.job_search_state_repository import JobSearchStateRepository


class JobSearchStatusInput(BaseModel):
    pass


class JobSearchStatusTool(BaseTool):
    name: str = "job_search_status"
    description: str = "Returns when jobs were last fetched and when the job search was first initialized."
    args_schema: Type[BaseModel] = JobSearchStatusInput
    state_repo: JobSearchStateRepository

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self) -> str:
        state = self.state_repo.get()
        if not state.last_searched_at:
            return "Job search has not been initialized yet."
        return f"Last search: {state.last_searched_at}"

    def _run(self) -> str:
        raise NotImplementedError("Use _arun")
