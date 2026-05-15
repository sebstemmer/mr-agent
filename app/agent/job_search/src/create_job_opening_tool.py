from typing import Type

from files.src.delete_file import DeleteFile
from files.src.parse_html_file_to_string import ParseHtmlFileToString
from job_search.src.job_opening_model import JobOpening
from job_search.src.job_opening_repository import JobOpeningRepository
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from utils.common.src.confirm import confirm
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

from agent.job_search.src.parse_job_opening import ParseJobOpening
from files.src.unsupported_file_type_error import UnsupportedFileTypeError

TOOL_NAME = "create_job_opening"


class CreateJobOpeningInput(BaseModel):
    file_uuid: str = Field(description="The uuid of the uploaded HTML file.")


class CreateJobOpeningTool(BaseTool):
    name: str = TOOL_NAME
    description: str = (
        "Creates a new job opening from an uploaded HTML file. "
        "Only call this when the user has uploaded an HTML file."
    )
    args_schema: Type[BaseModel] = CreateJobOpeningInput
    response_format: str = "content_and_artifact"
    job_opening_repo: JobOpeningRepository
    parse_html_file_to_string: ParseHtmlFileToString
    parse_job_opening: ParseJobOpening
    delete_file: DeleteFile

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, file_uuid: str) -> tuple[str, str]:
        try:
            html = await self.parse_html_file_to_string.parse(uuid=file_uuid)
        except UnsupportedFileTypeError as e:
            result = str(e)
            return result, result

        parsed = await self.parse_job_opening.parse(html=html)

        confirmation_text = (
            f"*Title*\n"
            f"{parsed.title}\n\n"
            f"*Summary*\n"
            f"{parsed.summary}\n\n"
            f"*Requirements*\n"
            f"{parsed.requirements}\n\n"
            f"*Company link*\n"
            f"{parsed.link_to_company}\n\n"
            f"Save this job opening?"
        )

        if not confirm(question=confirmation_text):
            await self.delete_file.delete(uuid=file_uuid)
            result = "Job opening discarded."
            return result, result

        job_opening = await self.job_opening_repo.save(
            job_opening=JobOpening(
                title=parsed.title,
                summary=parsed.summary,
                requirements=parsed.requirements,
                link_to_company=parsed.link_to_company,
            ),
        )

        result = f"Job opening created (id={job_opening.id})."
        return result, result

    def _run(self, file_uuid: str) -> str:
        raise SyncRunNotImplemented()
