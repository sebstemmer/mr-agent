from langchain_core.tools import BaseTool
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented


class HandleJobSearchTool(BaseTool):
    name: str = "handle_job_search"
    description: str = "Handles job search related questions."

    async def _arun(self, **kwargs) -> None:
        pass

    def _run(self, **kwargs) -> None:
        raise SyncRunNotImplemented()
