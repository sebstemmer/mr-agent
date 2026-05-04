from logging import Logger

from agent.state.agent_state import Branch, BranchResult
from agent.weather.src.get_weather_tool import GetWeatherTool
from utils.common.src.unknown_tool_called import UnknownToolCalled

from agent_v2.agent.agent_state import AgentState

HANDLE_WEATHER_NODE_NAME = "weather"


class GetWeatherNode:
    def __init__(
        self,
        get_weather_tool: GetWeatherTool,
        logger: Logger,
    ):
        self._get_weather_tool = get_weather_tool
        self._logger = logger

    async def handle(self, state: AgentState) -> dict:
        await self._get_weather_tool.ainvoke(input=response.tool_calls[0]["args"])

        response = await self._llm.ainvoke(messages=state.messages)

        if not response.tool_calls:
            self._logger.info("[branch=%s] text response", HANDLE_WEATHER_NODE_NAME)
            visible_result = response.content
        elif (
            tool_name := response.tool_calls[0]["name"]
        ) == self._get_weather_tool.name:
            self._logger.info(
                "[branch=%s] tool=%s", HANDLE_WEATHER_NODE_NAME, tool_name
            )
            visible_result = await self._get_weather_tool.ainvoke(
                input=response.tool_calls[0]["args"]
            )
        else:
            raise UnknownToolCalled(tool_name=response.tool_calls[0]["name"])

        return {
            "branch_results": [
                BranchResult(branch=Branch.WEATHER, visible_result=visible_result)
            ],
        }
