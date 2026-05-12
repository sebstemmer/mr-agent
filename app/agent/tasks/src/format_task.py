from datetime import date


def format_task(task: dict) -> str:
    line = task["title"]
    due_raw = task.get("dueDateTime", {}).get("dateTime")
    if due_raw:
        line += f" - due: {date.fromisoformat(due_raw[:10]).strftime('%Y-%m-%d')}"
    recurrence = task.get("recurrence")
    if recurrence:
        line += f" (recurring: {recurrence['pattern']['type']})"
    completed_raw = (task.get("completedDateTime") or {}).get("dateTime")
    if completed_raw:
        line += f" - completed: {date.fromisoformat(completed_raw[:10]).strftime('%Y-%m-%d')}"
    return line
