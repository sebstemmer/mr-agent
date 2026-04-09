from langchain_core.tools import BaseTool
from utils.src.sync_run_not_implemented import SyncRunNotImplemented


class HandleWeatherTool(BaseTool):
    name: str = "handle_weather"
    description: str = "Handles weather-related questions."

    async def _arun(self, **kwargs) -> None:
        pass

    def _run(self, **kwargs) -> None:
        raise SyncRunNotImplemented()
