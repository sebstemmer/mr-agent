from datetime import datetime
from typing import Type

from langchain_core.tools import BaseTool
from microsoft_todo.src.microsoft_todo_client import MicrosoftTodoClient
from pydantic import BaseModel, Field
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented


class _RecurrencePattern(BaseModel):
    type: str = Field(
        description=(
            "Pattern type: "
            "'daily' (e.g. every day, every 3 days), "
            "'weekly' (e.g. every Monday, every week on Mon and Fri), "
            "'absoluteMonthly' (same date each month, e.g. every 15th)."
        ),
    )
    interval: int = Field(
        description=(
            "Number of units between occurrences. "
            "1 = every (every day, every week, every month), "
            "2 = every other (every other day, every 2 weeks), "
            "3 = every third, etc. The unit is determined by the type field."
        ),
    )
    days_of_week: list[str] | None = Field(
        default=None,
        description=(
            "Days of the week when the task recurs. Only used for 'weekly' type, ignored otherwise. "
            "Values: 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'. "
            "Examples: ['monday'] for every Monday, ['monday', 'friday'] for twice a week."
        ),
    )


class _Recurrence(BaseModel):
    pattern: _RecurrencePattern
    start_date: str = Field(description="Start date in YYYY-MM-DD format.")


class CreateTaskInput(BaseModel):
    title: str = Field(description="The title of the task to create.")
    due_datetime: str | None = Field(
        default=None,
        description="Optional due date and time in ISO 8601 format (e.g. 2026-04-15T14:00:00).",
    )
    recurrence: _Recurrence | None = Field(
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
    name: str = "create_task"
    description: str = "Creates a new task in the user's personal todo list."
    args_schema: Type[BaseModel] = CreateTaskInput
    todo_client: MicrosoftTodoClient

    class Config:
        arbitrary_types_allowed = True

    async def _arun(
        self,
        title: str,
        due_datetime: str | None = None,
        recurrence: _Recurrence | None = None,
    ) -> str:
        parsed_dt = datetime.fromisoformat(due_datetime) if due_datetime else None
        parsed_recurrence = self._build_recurrence(recurrence=recurrence) if recurrence else None
        await self.todo_client.save(
            title=title,
            due_datetime=parsed_dt,
            recurrence=parsed_recurrence,
        )
        return f"Created task: {title}"

    def _run(self, title: str, **_kwargs) -> str:
        raise SyncRunNotImplemented()

    @staticmethod
    def _build_recurrence(recurrence: _Recurrence) -> dict:
        pattern: dict = {
            "type": recurrence.pattern.type,
            "interval": recurrence.pattern.interval,
        }
        if recurrence.pattern.days_of_week is not None:
            pattern["daysOfWeek"] = recurrence.pattern.days_of_week
        return {
            "pattern": pattern,
            "range": {
                "type": "noEnd",
                "startDate": recurrence.start_date,
            },
        }
