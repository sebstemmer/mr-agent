from typing import Type

from langchain_core.tools import BaseTool
from microsoft_todo.src.microsoft_todo_client import MicrosoftTodoClient
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

from agent.tasks.src.task_lists import AVAILABLE_LISTS

TOOL_NAME = "delete_task"


class DeleteTaskInput(BaseModel):
    list_name: str = Field(
        description=f"Name of the task list to delete the task from. Available: {AVAILABLE_LISTS}.",
    )
    task_id: str = Field(
        description="The 'task_id' from the conversation context, not the index."
    )
    title: str = Field(description="The title of the task to delete.")


class DeleteTaskTool(BaseTool):
    name: str = TOOL_NAME
    description: str = "Permanently deletes a task from a task list."
    args_schema: Type[BaseModel] = DeleteTaskInput
    response_format: str = "content_and_artifact"
    todo_client: MicrosoftTodoClient
    list_name_to_id: dict[str, str]

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, list_name: str, task_id: str, title: str) -> tuple[str, str]:
        list_id = self.list_name_to_id[list_name]
        await self.todo_client.delete_by_id(list_id=list_id, task_id=task_id)
        return f"Deleted task {task_id}.", f"Deleted task '{title}'."

    def _run(self, **_kwargs) -> str:
        raise SyncRunNotImplemented()
