from pydantic import BaseModel, Field


class RecurrencePattern(BaseModel):
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


class Recurrence(BaseModel):
    pattern: RecurrencePattern
    start_date: str = Field(description="Start date in YYYY-MM-DD format.")


def build_recurrence(recurrence: Recurrence) -> dict:
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
