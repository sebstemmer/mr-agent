from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel
from utils.src.sync_run_not_implemented import SyncRunNotImplemented

from job_search.src.job_search_state_repository import JobSearchStateRepository


class JobSearchStatusInput(BaseModel):
    pass


class JobSearchStatusTool(BaseTool):
    name: str = "job_search_status"
    description: str = (
        "Returns the timestamp of the last job search. Only call this when the user "
        "explicitly asks when jobs were last fetched or about the search status. "
        "Never call this as a fallback when other tools cannot be called."
    )
    args_schema: Type[BaseModel] = JobSearchStatusInput
    state_repo: JobSearchStateRepository

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self) -> str:
        state = await self.state_repo.find()
        if not state or not state.last_searched_at:
            return "Job search has not been initialized yet."
        return f"Last search: {state.last_searched_at}"

    def _run(self) -> str:
        raise SyncRunNotImplemented()
