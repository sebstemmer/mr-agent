from datetime import date
from typing import Type

from langchain_core.tools import BaseTool
from microsoft_todo.src.microsoft_todo_client import MicrosoftTodoClient
from pydantic import BaseModel, Field
from utils.common.src.datetime_utils import today_berlin
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

from agent.tasks.recurrence import Recurrence, build_recurrence

_TOOL_NAME = "create_task"


class CreateTaskInput(BaseModel):
    title: str = Field(description="The title of the task to create.")
    due_date: str | None = Field(
        default=None,
        description="Due date in YYYY-MM-DD format (e.g. 2026-04-15). Required when recurrence is set.",
    )
    recurrence: Recurrence | None = Field(
        default=None,
        description=(
            "Optional recurrence for repeating tasks. Examples: "
            "'every day' → type='daily', interval=1. "
            "'every 3 days' → type='daily', interval=3. "
            "'every Monday' → type='weekly', interval=1, days_of_week=['monday']. "
            "'every other week on Mon and Fri' → type='weekly', interval=2, days_of_week=['monday', 'friday']. "
            "'every month on the 15th' → type='absoluteMonthly', interval=1."
        ),
    )


class CreateTaskTool(BaseTool):
    name: str = _TOOL_NAME
    description: str = "Creates a new task in the user's personal todo list."
    args_schema: Type[BaseModel] = CreateTaskInput
    response_format: str = "content_and_artifact"
    todo_client: MicrosoftTodoClient

    class Config:
        arbitrary_types_allowed = True

    async def _arun(
        self,
        title: str,
        due_date: str | None = None,
        recurrence: Recurrence | None = None,
    ) -> tuple[str, str]:
        if recurrence and not due_date:
            due_date = today_berlin().isoformat()
        parsed_date = date.fromisoformat(due_date) if due_date else None
        parsed_recurrence = (
            build_recurrence(recurrence=recurrence) if recurrence else None
        )
        await self.todo_client.save(
            title=title,
            due_date=parsed_date,
            recurrence=parsed_recurrence,
        )
        message = f"Created task: {title}"
        return message, message

    def _run(self, title: str, **_kwargs) -> str:
        raise SyncRunNotImplemented()
