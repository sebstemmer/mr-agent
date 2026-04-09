from langchain_core.tools import BaseTool
from utils.src.sync_run_not_implemented import SyncRunNotImplemented


class HandleConversationTool(BaseTool):
    name: str = "handle_conversation"
    description: str = (
        "Handles general conversation that is not related to a specific domain."
    )

    async def _arun(self, **kwargs) -> None:
        pass

    def _run(self, **kwargs) -> None:
        raise SyncRunNotImplemented()
