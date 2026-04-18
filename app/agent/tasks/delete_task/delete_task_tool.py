from typing import Type

from langchain_core.tools import BaseTool
from microsoft_todo.src.microsoft_todo_client import MicrosoftTodoClient
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented


_TOOL_NAME = "delete_task"


class DeleteTaskInput(BaseModel):
    task_id: str = Field(description="The task ID from a previous get_tasks result.")
    title: str = Field(description="The title of the task to delete.")


class DeleteTaskTool(BaseTool):
    name: str = _TOOL_NAME
    description: str = (
        "Permanently deletes a task from the user's personal todo list. "
        "Use the task ID from a previous get_tasks result."
    )
    args_schema: Type[BaseModel] = DeleteTaskInput
    response_format: str = "content_and_artifact"
    todo_client: MicrosoftTodoClient

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, task_id: str, title: str) -> tuple[str, str]:
        await self.todo_client.delete_by_id(task_id=task_id)

        return f"Deleted task {task_id}.", f"Deleted task '{title}'."

    def _run(self, **_kwargs) -> str:
        raise SyncRunNotImplemented()
