from logging import Logger

from langchain_core.messages import AIMessage, BaseMessage
from utils.common.src.llm_builder import LlmBuilder
from utils.common.src.unknown_tool_called import UnknownToolCalled

from agent.state.agent_state import Branch, BranchResult
from agent.weather.src.get_weather_tool import GetWeatherTool

HANDLE_WEATHER_NODE_NAME = "weather"


class HandleWeatherNode:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        get_weather_tool: GetWeatherTool,
        logger: Logger,
    ):
        self._get_weather_tool = get_weather_tool
        self._logger = logger
        self._llm = (
            LlmBuilder(api_key=api_key, model=model)
            .system_prompt(system_prompt)
            .tools(
                tools=[get_weather_tool],
                tool_choice="auto",
                parallel_tool_calls=False,
            )
            .instruction(
                "You have been selected to handle the weather-related part"
                " of the user's request."
            )
            .build()
        )

    async def handle(self, messages: list[BaseMessage]) -> dict:
        response = await self._llm.ainvoke(messages=messages)

        if not response.tool_calls:
            self._logger.info("[branch=%s] text response", HANDLE_WEATHER_NODE_NAME)
            visible_result = response.content
        elif (tool_name := response.tool_calls[0]["name"]) == self._get_weather_tool.name:
            self._logger.info("[branch=%s] tool=%s", HANDLE_WEATHER_NODE_NAME, tool_name)
            visible_result = await self._get_weather_tool.ainvoke(input=response.tool_calls[0]["args"])
        else:
            raise UnknownToolCalled(tool_name=response.tool_calls[0]["name"])

        return {
            "branch_results": [
                BranchResult(branch=Branch.WEATHER, visible_result=visible_result)
            ],
        }
