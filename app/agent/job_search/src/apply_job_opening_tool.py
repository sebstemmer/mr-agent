from datetime import date
from typing import Type

from job_search.src.apply_job_opening import ApplyJobOpening
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

TOOL_NAME = "apply_job_opening"


class ApplyJobOpeningInput(BaseModel):
    job_opening_uuid: str = Field(description="The 'uuid' of the job opening from the conversation context.")
    applied_at: str = Field(description="The date the user applied in YYYY-MM-DD format.")
    asked_salary: str = Field(description="The salary the user asked for (e.g. '75k', '80-90k').")
    application_file_uuid: str = Field(description="The 'uuid' of the uploaded application PDF file.")
    link_to_job_opening: str | None = Field(default=None, description="The URL link to the job opening posting, if available.")


class ApplyJobOpeningTool(BaseTool):
    name: str = TOOL_NAME
    description: str = (
        "Marks a job opening as applied. "
        "Requires the job opening uuid, the asked salary, and the uuid of the uploaded application PDF."
    )
    args_schema: Type[BaseModel] = ApplyJobOpeningInput
    response_format: str = "content_and_artifact"
    apply_job_opening: ApplyJobOpening

    class Config:
        arbitrary_types_allowed = True

    async def _arun(
        self, job_opening_uuid: str, applied_at: str, asked_salary: str,
        application_file_uuid: str, link_to_job_opening: str | None = None,
    ) -> tuple[str, str]:
        job_opening = await self.apply_job_opening.apply(
            uuid=job_opening_uuid,
            applied_at=date.fromisoformat(applied_at),
            asked_salary=asked_salary,
            link_to_job_opening=link_to_job_opening,
            application_file_uuid=application_file_uuid,
        )
        context = f"Applied for job opening {job_opening.uuid}."
        readable = f"Applied for '{job_opening.title}'."
        return context, readable

    def _run(self, **_kwargs) -> str:
        raise SyncRunNotImplemented()
