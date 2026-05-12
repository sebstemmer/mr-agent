from dataclasses import dataclass


@dataclass
class TaskList:
    name: str
    description: str


PERSONAL_TASKS = TaskList(
    name="personal tasks",
    description="personal task list with day-to-day tasks and to-dos",
)

AVAILABLE_LISTS = ", ".join(
    f"'{t.name}' ({t.description})" for t in [PERSONAL_TASKS]
)
