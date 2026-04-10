from logging import Logger
from typing import Type

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from utils.src.llm_with_system_prompt import LlmWithSystemPrompt
from utils.src.sync_run_not_implemented import SyncRunNotImplemented
from utils.src.unknown_tool_called import UnknownToolCalled

from weather.src.get_weather_tool import GetWeatherTool

WEATHER_BRANCH = "weather"
LEAVE_WEATHER_BRANCH_TOOL_NAME = "leave_weather_branch"


class _LeaveInput(BaseModel):
    pass


class _LeaveWeatherBranchTool(BaseTool):
    name: str = LEAVE_WEATHER_BRANCH_TOOL_NAME
    description: str = (
        "Use when the user has changed topic and is no longer asking about weather."
    )
    args_schema: Type[BaseModel] = _LeaveInput

    async def _arun(self) -> None:
        pass

    def _run(self) -> None:
        raise SyncRunNotImplemented()


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
            tools=[get_weather_tool, _LeaveWeatherBranchTool()],
            tool_choice="auto",
        )

    async def handle(self, messages: list[BaseMessage]) -> dict:
        self._logger.info("[branch=%s] handling", WEATHER_BRANCH)
        response = await self._llm.ainvoke(messages=messages)

        if not response.tool_calls:
            self._logger.info("[branch=%s] text response", WEATHER_BRANCH)
            return {
                "messages": [AIMessage(content=response.content)],
                "current_branch": WEATHER_BRANCH,
            }

        # noinspection PyTypeChecker
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        self._logger.info("[branch=%s] tool=%s", WEATHER_BRANCH, tool_name)

        if tool_name == LEAVE_WEATHER_BRANCH_TOOL_NAME:
            return {"current_branch": None}

        if tool_name == self._get_weather_tool.name:
            result = await self._get_weather_tool.ainvoke(input=tool_call["args"])
            return {
                "messages": [AIMessage(content=result)],
                "current_branch": WEATHER_BRANCH,
            }

        raise UnknownToolCalled(tool_name=tool_name)
