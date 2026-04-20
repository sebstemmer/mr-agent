from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

_TOOL_NAME = "chat_about_tasks"


class ChatAboutTasksInput(BaseModel):
    message: str = Field(
        description="Your response to the user about their tasks."
    )


class ChatAboutTasksTool(BaseTool):
    name: str = _TOOL_NAME
    description: str = (
        "Use to respond to the user about task-related questions, "
        "observations, or anything related to their todo list."
    )
    args_schema: Type[BaseModel] = ChatAboutTasksInput

    async def _arun(self, message: str) -> None:
        pass

    def _run(self, **_kwargs) -> None:
        raise SyncRunNotImplemented()
