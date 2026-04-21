from logging import Logger

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import BaseTool
from langgraph.types import Command
from utils.common.src.llm_with_system_prompt import LlmWithSystemPrompt

from agent.job_search.src.handle_job_search_node import JOB_SEARCH_BRANCH
from agent.job_search.src.handle_job_search_tool import TOOL_NAME as _JOB_SEARCH_TOOL
from agent.tasks.create_tasks_subgraph import PERSONAL_TASKS_LIST_BRANCH
from agent.tasks.personal_task_list_tool import TOOL_NAME as _PERSONAL_TASK_LIST_TOOL
from agent.weather.src.handle_weather_node import WEATHER_BRANCH
from agent.weather.src.handle_weather_tool import TOOL_NAME as _WEATHER_TOOL

_TOOL_NAME_TO_BRANCH: dict[str, str] = {
    _WEATHER_TOOL: WEATHER_BRANCH,
    _JOB_SEARCH_TOOL: JOB_SEARCH_BRANCH,
    _PERSONAL_TASK_LIST_TOOL: PERSONAL_TASKS_LIST_BRANCH,
}

_END = "__end__"


class RouterNode:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        tools: list[BaseTool],
        logger: Logger,
    ):
        self._logger = logger
        self._llm = LlmWithSystemPrompt(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=False,
            additional_instructions=None,
        )

    async def route(self, messages: list[BaseMessage]) -> Command:
        response = await self._llm.ainvoke(messages=messages)

        if not response.tool_calls:
            self._logger.info("[router] text response")
            return Command(
                update={"messages": [AIMessage(content=response.content)]},
                goto=_END,
            )

        # noinspection PyTypeChecker
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        branch = _TOOL_NAME_TO_BRANCH[tool_name]
        self._logger.info("[router] tool=%s branch=%s", tool_name, branch)

        return Command(goto=branch)
