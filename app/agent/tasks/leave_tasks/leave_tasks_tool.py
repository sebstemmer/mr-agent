from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

_TOOL_NAME = "leave_tasks_branch"


class LeaveTasksInput(BaseModel):
    pass


class LeaveTasksTool(BaseTool):
    name: str = _TOOL_NAME
    description: str = (
        "Use when the user has changed topic and is no longer asking about tasks on the todo list."
    )
    args_schema: Type[BaseModel] = LeaveTasksInput

    async def _arun(self) -> None:
        pass

    def _run(self) -> None:
        raise SyncRunNotImplemented()
