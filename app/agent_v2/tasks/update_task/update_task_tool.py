from datetime import date
from typing import Type

from langchain_core.tools import BaseTool
from microsoft_todo.src.microsoft_todo_client import MicrosoftTodoClient
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented
from utils.common.src.update_field import StaysTheSame, Update

from agent.tasks.format_task import format_task

_TOOL_NAME = "update_task"


class UpdateTaskInput(BaseModel):
    task_id: str = Field(description="The 'task_id' from the conversation context, not the index.")
    title: str | None = Field(
        default=None,
        description="New title for the task. Only provide if the user wants to change it.",
    )
    due_date: str | None = Field(
        default=None,
        description="New due date in YYYY-MM-DD format. Mutually exclusive with remove_due_date.",
    )
    remove_due_date: bool = Field(
        default=False,
        description="Set to true to remove the due date. Mutually exclusive with due_date.",
    )


class UpdateTaskTool(BaseTool):
    name: str = _TOOL_NAME
    description: str = (
        "Updates an existing task in the user's personal todo list. "
        "Can change title or due date."
    )
    args_schema: Type[BaseModel] = UpdateTaskInput
    response_format: str = "content_and_artifact"
    todo_client: MicrosoftTodoClient

    class Config:
        arbitrary_types_allowed = True

    async def _arun(
        self,
        task_id: str,
        title: str | None = None,
        due_date: str | None = None,
        remove_due_date: bool = False,
    ) -> tuple[str, str]:
        task = await self.todo_client.update_by_id(
            task_id=task_id,
            title=Update(value=title) if title is not None else StaysTheSame(),
            due_date=(
                Update(value=None)
                if remove_due_date
                else Update(value=date.fromisoformat(due_date))
                if due_date is not None
                else StaysTheSame()
            ),
            status=StaysTheSame(),
            completed_date=StaysTheSame(),
        )

        context = f"Updated task: id={task['id']}, title={task['title']}"
        user_content = f"Updated: {format_task(task=task)}"
        return context, user_content

    def _run(self, **_kwargs) -> str:
        raise SyncRunNotImplemented()
