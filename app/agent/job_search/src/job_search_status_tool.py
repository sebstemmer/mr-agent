from typing import Type

from job_search.src.job_search_state_repository import JobSearchStateRepository
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

TOOL_NAME = "job_search_status"


class JobSearchStatusInput(BaseModel):
    pass


class JobSearchStatusTool(BaseTool):
    name: str = TOOL_NAME
    description: str = (
        "Returns the timestamp of the last job search. Only call this when the user "
        "explicitly asks when jobs were last fetched or about the search status."
    )
    args_schema: Type[BaseModel] = JobSearchStatusInput
    response_format: str = "content_and_artifact"
    state_repo: JobSearchStateRepository

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self) -> tuple[str, str]:
        state = await self.state_repo.find()
        if not state or not state.last_searched_at:
            message = "Job search has not been initialized yet."
        else:
            message = f"Last search: {state.last_searched_at}"
        return message, message

    def _run(self) -> str:
        raise SyncRunNotImplemented()
