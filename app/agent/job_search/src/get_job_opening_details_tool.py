from typing import Type

from job_search.src.job_opening_repository import JobOpeningRepository
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

TOOL_NAME = "get_job_opening_details"


class GetJobOpeningDetailsInput(BaseModel):
    uuid: str = Field(description="The 'uuid' of the job opening from the conversation context.")


class GetJobOpeningDetailsTool(BaseTool):
    name: str = TOOL_NAME
    description: str = "Gets all details of a specific job opening."
    args_schema: Type[BaseModel] = GetJobOpeningDetailsInput
    response_format: str = "content_and_artifact"
    job_opening_repo: JobOpeningRepository

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, uuid: str) -> tuple[str, str]:
        opening = await self.job_opening_repo.find_by_uuid(uuid=uuid)
        if opening is None:
            result = f"Job opening not found: {uuid}"
            return result, result

        context = f"Job opening details for uuid={opening.uuid}, title={opening.title}."
        readable = (
            f"*Title*\n"
            f"{opening.title}\n\n"
            f"*Summary*\n"
            f"{opening.summary}\n\n"
            f"*Requirements*\n"
            f"{opening.requirements}\n\n"
            f"*Company link*\n"
            f"{opening.link_to_company}\n\n"
            f"*Rating*\n"
            f"{opening.rating}/3\n\n"
            f"*Rating reason*\n"
            f"{opening.rating_reason}\n\n"
            f"*Applied*\n"
            f"{opening.applied}\n\n"
            f"*Applied at*\n"
            f"{opening.applied_at}\n\n"
            f"*Asked salary*\n"
            f"{opening.asked_salary}\n\n"
            f"*Application file*\n"
            f"{opening.application_file_uuid}\n\n"
            f"*Job opening link*\n"
            f"{opening.link_to_job_opening}"
        )
        return context, readable

    def _run(self, **_kwargs) -> str:
        raise SyncRunNotImplemented()
