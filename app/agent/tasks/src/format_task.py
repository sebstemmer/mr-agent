from datetime import date

_TYPE_TO_UNIT = {
    "daily": "day",
    "weekly": "week",
    "absoluteMonthly": "month",
}


def _format_recurrence(pattern: dict) -> str:
    interval = pattern.get("interval", 1)
    pattern_type = pattern["type"]
    unit = _TYPE_TO_UNIT.get(pattern_type, pattern_type)

    if interval == 1:
        base = f"{unit}ly" if unit != "month" else "monthly"
    else:
        base = f"every {interval} {unit}s"

    days = pattern.get("daysOfWeek")
    if days:
        abbreviated = [d[:3].capitalize() for d in days]
        base += f" on {', '.join(abbreviated)}"

    return base


def format_task(task: dict) -> str:
    line = task["title"]
    due_raw = task.get("dueDateTime", {}).get("dateTime")
    if due_raw:
        line += f" - due: {date.fromisoformat(due_raw[:10]).strftime('%Y-%m-%d')}"
    recurrence = task.get("recurrence")
    if recurrence:
        line += f" (recurring: {_format_recurrence(recurrence['pattern'])})"
    completed_raw = (task.get("completedDateTime") or {}).get("dateTime")
    if completed_raw:
        line += f" - completed: {date.fromisoformat(completed_raw[:10]).strftime('%Y-%m-%d')}"
    return line
