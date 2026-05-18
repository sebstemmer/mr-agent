from typing import Type

from job_search.src.job_opening_repository import JobOpeningRepository
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

TOOL_NAME = "delete_job_opening"


class DeleteJobOpeningInput(BaseModel):
    uuid: str = Field(description="The 'uuid' of the job opening from the conversation context.")
    title: str = Field(description="The title of the job opening to delete.")


class DeleteJobOpeningTool(BaseTool):
    name: str = TOOL_NAME
    description: str = "Permanently deletes a saved job opening."
    args_schema: Type[BaseModel] = DeleteJobOpeningInput
    response_format: str = "content_and_artifact"
    job_opening_repo: JobOpeningRepository

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, uuid: str, title: str) -> tuple[str, str]:
        await self.job_opening_repo.delete_by_uuid(uuid=uuid)
        return f"Deleted job opening {uuid}.", f"Deleted job opening '{title}'."

    def _run(self, **_kwargs) -> str:
        raise SyncRunNotImplemented()
