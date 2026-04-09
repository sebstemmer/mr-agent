from logging import Logger
from typing import Type

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from utils.src.sync_run_not_implemented import SyncRunNotImplemented

from weather.src.get_weather_tool import GetWeatherTool

WEATHER_BRANCH = "weather"


class _ResponseInput(BaseModel):
    response: str = Field(description="The response to send to the user")


class _StayInWeatherBranchTool(BaseTool):
    name: str = "stay_in_weather_branch"
    description: str = (
        "Use when the user is still in the context of weather but no other "
        "weather tool should be called. For example, asking the user for "
        "missing information needed to call a tool."
    )
    args_schema: Type[BaseModel] = _ResponseInput

    async def _arun(self, response: str) -> str:
        return response

    def _run(self, response: str) -> str:
        raise SyncRunNotImplemented()


class _LeaveWeatherBranchTool(BaseTool):
    name: str = "leave_weather_branch"
    description: str = (
        "Use when the user has changed topic and is no longer asking about weather."
    )
    args_schema: Type[BaseModel] = _ResponseInput

    async def _arun(self, response: str) -> str:
        return response

    def _run(self, response: str) -> str:
        raise SyncRunNotImplemented()


class HandleWeather:
    def __init__(
        self,
        api_key: str,
        model: str,
        get_weather_tool: GetWeatherTool,
        logger: Logger,
    ):
        self._get_weather_tool = get_weather_tool
        self._logger = logger
        self._stay_tool = _StayInWeatherBranchTool()
        self._leave_tool = _LeaveWeatherBranchTool()

        # noinspection PyTypeChecker
        llm = ChatOpenAI(api_key=api_key, model=model)

        self._llm = llm.bind_tools(
            [get_weather_tool, self._stay_tool, self._leave_tool],
            tool_choice="required",
        )

    async def handle(self, messages: list[BaseMessage]) -> dict:
        self._logger.info("[branch=%s] handling", WEATHER_BRANCH)
        response = await self._llm.ainvoke(messages)

        # noinspection PyTypeChecker
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        self._logger.info("[branch=%s] tool=%s", WEATHER_BRANCH, tool_name)

        if tool_name == "get_weather":
            result = await self._get_weather_tool.ainvoke(input=tool_call["args"])
            return {"messages": [AIMessage(content=result)], "current_branch": WEATHER_BRANCH}

        if tool_name == "stay_in_weather_branch":
            return {
                "messages": [AIMessage(content=tool_call["args"]["response"])],
                "current_branch": WEATHER_BRANCH,
            }

        return {"current_branch": None}
