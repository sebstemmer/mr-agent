from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented


class SendEmailInput(BaseModel):
    recipient: str = Field(description="Email address of the recipient.")
    subject: str = Field(description="Subject line of the email.")
    body: str = Field(description="Body content of the email.")


TOOL_NAME = "send_email"


class SendEmailTool(BaseTool):
    name: str = TOOL_NAME
    description: str = "Sends an email to a given recipient."
    args_schema: Type[BaseModel] = SendEmailInput
    response_format: str = "content_and_artifact"

    async def _arun(self, recipient: str, subject: str, body: str) -> tuple[str, str]:
        return f"Email sent to {recipient}", f"Sent '{subject}' to {recipient}"

    def _run(self, recipient: str, subject: str, body: str) -> str:
        raise SyncRunNotImplemented()
