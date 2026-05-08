import json
from datetime import date
from typing import Type

from langchain_core.tools import BaseTool
from microsoft_todo.src.microsoft_todo_client import MicrosoftTodoClient
from microsoft_todo.src.task_status import TaskStatus
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

from agent_v2.tasks.src.format_task import format_task
from agent_v2.tasks.src.task_lists import AVAILABLE_LISTS

TOOL_NAME = "get_tasks"


class GetTasksInput(BaseModel):
    list_name: str = Field(
        description=f"Name of the task list to fetch from. Available: {AVAILABLE_LISTS}.",
    )
    status: str = Field(
        default=TaskStatus.NOT_STARTED,
        description=(
            f"Task status to filter by: "
            f"'{TaskStatus.NOT_STARTED}' (open tasks) or '{TaskStatus.COMPLETED}' (done). "
        ),
    )
    due_from: str | None = Field(
        default=None,
        description=(
            "Optional inclusive start of due date range in YYYY-MM-DD format. "
            "Examples: 'today' → today's date, 'this week' → Monday of this week."
        ),
    )
    due_to: str | None = Field(
        default=None,
        description=(
            "Optional inclusive end of due date range in YYYY-MM-DD format. "
            "Examples: 'today' → today's date, 'this week' → Sunday of this week, "
            "'tomorrow' → tomorrow's date."
        ),
    )


class GetTasksTool(BaseTool):
    name: str = TOOL_NAME
    description: str = (
        "Gets tasks from a task list. Can filter by status and due date range."
    )
    args_schema: Type[BaseModel] = GetTasksInput
    response_format: str = "content_and_artifact"
    todo_client: MicrosoftTodoClient
    list_name_to_id: dict[str, str]

    class Config:
        arbitrary_types_allowed = True

    async def _arun(
        self,
        list_name: str,
        status: str = TaskStatus.NOT_STARTED,
        due_from: str | None = None,
        due_to: str | None = None,
    ) -> tuple[str, str]:
        list_id = self.list_name_to_id[list_name]
        parsed_from = date.fromisoformat(due_from) if due_from else None
        parsed_to = date.fromisoformat(due_to) if due_to else None
        tasks = await self.todo_client.find_by_status_and_due_date_between_inclusive(
            list_id=list_id,
            status=TaskStatus(status),
            due_from=parsed_from,
            due_to=parsed_to,
        )
        if not tasks:
            return "No tasks found.", "No tasks found."

        context = json.dumps(
            [
                {
                    "index": index,
                    "task_id": task["id"],
                    "title": task["title"],
                }
                for index, task in enumerate(tasks, start=1)
            ]
        )
        user_content = self._format_tasks(tasks=tasks)
        return context, user_content

    def _run(self, **_kwargs) -> str:
        raise SyncRunNotImplemented()

    @staticmethod
    def _format_tasks(tasks: list[dict]) -> str:
        lines = []
        for index, task in enumerate(tasks, start=1):
            lines.append(f"{index}. {format_task(task=task)}")
        return "\n".join(lines)
