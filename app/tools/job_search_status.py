from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from repositories.search_state_repository import SearchStateRepository


class JobSearchStatusInput(BaseModel):
    pass


class JobSearchStatusTool(BaseTool):
    name: str = "job_search_status"
    description: str = "Returns when jobs were last fetched and when the job search was first initialized."
    args_schema: Type[BaseModel] = JobSearchStatusInput
    state_repo: SearchStateRepository

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self) -> str:
        state = self.state_repo.get()
        if not state.initialized_at:
            return "Job search has not been initialized yet."
        return f"Last search: {state.last_search}"

    def _run(self) -> str:
        raise NotImplementedError("Use _arun")
