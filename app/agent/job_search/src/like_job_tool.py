from typing import Type

from job_search.src.like_job import LikeJob
from langchain_core.tools import BaseTool
from langgraph.types import interrupt
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented


class LikeJobInput(BaseModel):
    public_id: str = Field(description="The public id of the job posting to like.")


class LikeJobTool(BaseTool):
    name: str = "like_job"
    description: str = (
        "Marks a job posting as liked by the user. Ask the user for the public id "
        "of the job they want to like. Requires human confirmation before applying."
    )
    args_schema: Type[BaseModel] = LikeJobInput
    like_job: LikeJob

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, public_id: str) -> str:
        answer = interrupt(
            {"question": f"Do you want to like job posting with id {public_id}?"}
        )

        if str(answer).strip().lower() not in ("yes", "y"):
            return f"Skipped liking job {public_id}."

        await self.like_job.like(public_id=public_id)
        return f"Liked job {public_id}."

    def _run(self, public_id: str) -> str:
        raise SyncRunNotImplemented()
