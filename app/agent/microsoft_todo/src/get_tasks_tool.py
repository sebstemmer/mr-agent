import json
from datetime import date, datetime
from typing import Type

from langchain_core.tools import BaseTool
from microsoft_todo.src.microsoft_todo_client import MicrosoftTodoClient
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented


class _GetTasksInput(BaseModel):
    status: str = Field(
        description="Task status to filter by: 'notStarted' (open tasks) or 'completed' (done).",
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
    name: str = "get_tasks"
    description: str = "Gets tasks from the user's personal todo list. Can filter by status and due date range."
    args_schema: Type[BaseModel] = _GetTasksInput
    response_format: str = "content_and_artifact"
    todo_client: MicrosoftTodoClient

    class Config:
        arbitrary_types_allowed = True

    async def _arun(
        self,
        status: str,
        due_from: str | None = None,
        due_to: str | None = None,
    ) -> tuple[str, str]:
        parsed_from = date.fromisoformat(due_from) if due_from else None
        parsed_to = date.fromisoformat(due_to) if due_to else None
        tasks = await self.todo_client.find_by_status_and_due_date_between_inclusive(
            status=status,
            due_from=parsed_from,
            due_to=parsed_to,
        )
        if not tasks:
            return "No tasks found.", "No tasks found."

        context = json.dumps(
            [
                {
                    "number": index,
                    "id": task["id"],
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
            due_raw = task.get("dueDateTime", {}).get("dateTime")
            if due_raw:
                parsed_due = datetime.fromisoformat(due_raw)
                fmt = (
                    "%Y-%m-%d %H:%M"
                    if parsed_due.hour or parsed_due.minute
                    else "%Y-%m-%d"
                )
                due_str = f" - due: {parsed_due.strftime(fmt)}"
            else:
                due_str = ""
            recurrence = task.get("recurrence")
            recurrence_str = (
                f" (recurring: {recurrence['pattern']['type']})" if recurrence else ""
            )
            lines.append(f"{index}. {task['title']}{due_str}{recurrence_str}")
        return "\n".join(lines)
