from datetime import date
from typing import Type

from langchain_core.tools import BaseTool
from microsoft_todo.src.microsoft_todo_client import MicrosoftTodoClient
from microsoft_todo.src.task_status import TaskStatus
from pydantic import BaseModel, Field
from utils.common.src.datetime_utils import today_berlin
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented
from utils.common.src.update_field import StaysTheSame, Update

from agent_v2.tasks.src.format_task import format_task
from agent_v2.tasks.src.task_lists import AVAILABLE_LISTS

TOOL_NAME = "update_task"


class UpdateTaskInput(BaseModel):
    list_name: str = Field(
        description=f"Name of the task list. Available: {AVAILABLE_LISTS}.",
    )
    task_id: str = Field(
        description="The 'task_id' from the conversation context, not the index.",
    )
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
    complete: bool = Field(
        default=False,
        description="Set to true to mark the task as completed.",
    )
    completed_date: str | None = Field(
        default=None,
        description="Date the task was completed in YYYY-MM-DD format. Only used when complete=true. Defaults to today.",
    )


class UpdateTaskTool(BaseTool):
    name: str = TOOL_NAME
    description: str = (
        "Updates an existing task in a task list. "
        "Can change title, due date, or mark as completed. "
        "To complete a task, set complete=true."
    )
    args_schema: Type[BaseModel] = UpdateTaskInput
    response_format: str = "content_and_artifact"
    todo_client: MicrosoftTodoClient
    list_name_to_id: dict[str, str]

    class Config:
        arbitrary_types_allowed = True

    async def _arun(
        self,
        list_name: str,
        task_id: str,
        title: str | None = None,
        due_date: str | None = None,
        remove_due_date: bool = False,
        complete: bool = False,
        completed_date: str | None = None,
    ) -> tuple[str, str]:
        list_id = self.list_name_to_id[list_name]

        task = await self.todo_client.update_by_id(
            list_id=list_id,
            task_id=task_id,
            title=Update(value=title) if title is not None else StaysTheSame(),
            due_date=(
                Update(value=None)
                if remove_due_date
                else Update(value=date.fromisoformat(due_date))
                if due_date is not None
                else StaysTheSame()
            ),
            status=Update(value=TaskStatus.COMPLETED) if complete else StaysTheSame(),
            completed_date=(
                Update(value=date.fromisoformat(completed_date) if completed_date else today_berlin())
                if complete
                else StaysTheSame()
            ),
        )

        formatted = format_task(task=task)
        if complete:
            return f"Completed task: id={task['id']}, title={task['title']}", f"Completed: {formatted}"
        return f"Updated task: id={task['id']}, title={task['title']}", f"Updated: {formatted}"

    def _run(self, **_kwargs) -> str:
        raise SyncRunNotImplemented()
