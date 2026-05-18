import json
from typing import Type

from job_search.src.job_opening_repository import JobOpeningRepository
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

TOOL_NAME = "get_job_openings"


class GetJobOpeningsInput(BaseModel):
    pass


class GetJobOpeningsTool(BaseTool):
    name: str = TOOL_NAME
    description: str = "Gets all saved job openings."
    args_schema: Type[BaseModel] = GetJobOpeningsInput
    response_format: str = "content_and_artifact"
    job_opening_repo: JobOpeningRepository

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self) -> tuple[str, str]:
        job_openings = await self.job_opening_repo.find_all()
        if not job_openings:
            return "No job openings found.", "No job openings found."

        context = json.dumps(
            [
                {
                    "index": index,
                    "uuid": opening.uuid,
                    "title": opening.title,
                    "rating": opening.rating,
                }
                for index, opening in enumerate(job_openings, start=1)
            ]
        )
        readable = "\n".join(
            f"{index}. {opening.title}"
            for index, opening in enumerate(job_openings, start=1)
        )
        return context, readable

    def _run(self) -> str:
        raise SyncRunNotImplemented()
