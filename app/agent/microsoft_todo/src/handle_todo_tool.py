from langchain_core.tools import BaseTool
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented


class HandleTodoTool(BaseTool):
    name: str = "handle_todo"
    description: str = "Handles todo list related questions like adding, reading, or completing tasks."

    async def _arun(self, **kwargs) -> None:
        pass

    def _run(self, **kwargs) -> None:
        raise SyncRunNotImplemented()
