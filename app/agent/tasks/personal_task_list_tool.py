from langchain_core.tools import BaseTool
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented

TOOL_NAME = "personal_task_list"


class PersonalTaskListTool(BaseTool):
    name: str = TOOL_NAME
    description: str = "The user's personal task list. Supports adding, reading, updating, completing, and deleting tasks."

    async def _arun(self, **kwargs) -> None:
        pass

    def _run(self, **kwargs) -> None:
        raise SyncRunNotImplemented()
