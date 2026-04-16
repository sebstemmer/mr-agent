from typing import Type

from langchain_core.tools import BaseTool
from microsoft_todo.src.microsoft_todo_client import MicrosoftTodoClient
from microsoft_todo.src.task_status import TaskStatus
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented
from utils.common.src.update_field import StaysTheSame, Update

from agent.microsoft_todo.src.format_task import format_task


class _CompleteTaskInput(BaseModel):
    task_id: str = Field(description="The task ID from a previous get_tasks result.")


class CompleteTaskTool(BaseTool):
    name: str = "complete_task"
    description: str = (
        "Marks a task as completed in the user's personal todo list. "
        "Use the task ID from a previous get_tasks result."
    )
    args_schema: Type[BaseModel] = _CompleteTaskInput
    response_format: str = "content_and_artifact"
    todo_client: MicrosoftTodoClient

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, task_id: str) -> tuple[str, str]:
        task = await self.todo_client.update_by_id(
            task_id=task_id,
            title=StaysTheSame(),
            due_date=StaysTheSame(),
            status=Update(value=TaskStatus.COMPLETED),
        )

        context = f"Completed task: id={task['id']}, title={task['title']}"
        user_content = f"Completed: {format_task(task=task)}"
        return context, user_content

    def _run(self, **_kwargs) -> str:
        raise SyncRunNotImplemented()
