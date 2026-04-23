from logging import Logger

from langchain_core.messages import AIMessage, BaseMessage
from utils.common.src.llm_with_system_prompt import LlmWithSystemPrompt
from utils.common.src.unknown_tool_called import UnknownToolCalled

from agent.weather.src.get_weather_tool import GetWeatherTool

WEATHER_BRANCH = "weather"


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
        self._llm = LlmWithSystemPrompt(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            tools=[get_weather_tool],
            tool_choice="auto",
            parallel_tool_calls=False,
            additional_instructions=[
                "You are only responsible for weather-related requests."
                " Ignore anything unrelated to weather."
            ],
        )

    async def handle(self, messages: list[BaseMessage]) -> dict:
        self._logger.info("[branch=%s] handling", WEATHER_BRANCH)
        response = await self._llm.ainvoke(messages=messages)

        if not response.tool_calls:
            self._logger.info("[branch=%s] text response", WEATHER_BRANCH)
            return {"messages": [AIMessage(content=response.content)]}

        # noinspection PyTypeChecker
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        self._logger.info("[branch=%s] tool=%s", WEATHER_BRANCH, tool_name)

        if tool_name == self._get_weather_tool.name:
            result = await self._get_weather_tool.ainvoke(input=tool_call["args"])
            return {"messages": [AIMessage(content=result)]}

        raise UnknownToolCalled(tool_name=tool_name)
