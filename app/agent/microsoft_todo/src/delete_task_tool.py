from typing import Type

from langchain_core.tools import BaseTool
from microsoft_todo.src.microsoft_todo_client import MicrosoftTodoClient
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented


class _DeleteTaskInput(BaseModel):
    task_id: str = Field(description="The task ID from a previous get_tasks result.")


class DeleteTaskTool(BaseTool):
    name: str = "delete_task"
    description: str = (
        "Permanently deletes a task from the user's personal todo list. "
        "Use the task ID from a previous get_tasks result."
    )
    args_schema: Type[BaseModel] = _DeleteTaskInput
    response_format: str = "content_and_artifact"
    todo_client: MicrosoftTodoClient

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, task_id: str) -> tuple[str, str]:
        await self.todo_client.delete_by_id(task_id=task_id)

        message = "Task deleted."
        return message, message

    def _run(self, **_kwargs) -> str:
        raise SyncRunNotImplemented()
