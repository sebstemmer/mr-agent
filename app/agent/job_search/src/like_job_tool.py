from typing import Type

from job_search.src.like_job import LikeJob
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

TOOL_NAME = "like_job"


class LikeJobInput(BaseModel):
    public_id: str = Field(description="The public id of the job posting to like.")


class LikeJobTool(BaseTool):
    name: str = TOOL_NAME
    description: str = (
        "Marks a job posting as liked by the user. Call this tool whenever the user "
        "expresses intent to like a job (e.g. 'like job 3', 'I like that one'). "
        "Resolve the public_id from the most recent job listing in the conversation."
    )
    args_schema: Type[BaseModel] = LikeJobInput
    response_format: str = "content_and_artifact"
    like_job: LikeJob

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, public_id: str) -> tuple[str, str]:
        await self.like_job.like(public_id=public_id)
        message = f"Liked job {public_id}."
        return message, message

    def _run(self, **_kwargs) -> str:
        raise SyncRunNotImplemented()
