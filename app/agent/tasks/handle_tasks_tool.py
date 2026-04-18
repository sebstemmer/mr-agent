from langchain_core.tools import BaseTool
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented


class HandleTasksTool(BaseTool):
    name: str = "handle_tasks"
    description: str = "Handles tasks on the user's personal todo list, like adding, reading, updating, completing, or deleting tasks."

    async def _arun(self, **kwargs) -> None:
        pass

    def _run(self, **kwargs) -> None:
        raise SyncRunNotImplemented()
