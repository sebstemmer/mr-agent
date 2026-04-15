from logging import Logger

from langchain_core.messages import AIMessage, BaseMessage
from utils.common.src.llm_with_system_prompt import LlmWithSystemPrompt

from agent.job_search.src.handle_job_search_node import JOB_SEARCH_BRANCH
from agent.job_search.src.handle_job_search_tool import HandleJobSearchTool
from agent.microsoft_todo.src.handle_todo_node import TODO_BRANCH
from agent.microsoft_todo.src.handle_todo_tool import HandleTodoTool
from agent.weather.src.handle_weather_node import WEATHER_BRANCH
from agent.weather.src.handle_weather_tool import HandleWeatherTool

_TOOL_NAME_TO_BRANCH: dict[str, str] = {
    "handle_weather": WEATHER_BRANCH,
    "handle_job_search": JOB_SEARCH_BRANCH,
    "handle_todo": TODO_BRANCH,
}


class ClassifyIntentNode:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        handle_weather_tool: HandleWeatherTool,
        handle_job_search_tool: HandleJobSearchTool,
        handle_todo_tool: HandleTodoTool,
        logger: Logger,
    ):
        self._logger = logger
        self._llm = LlmWithSystemPrompt(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            tools=[handle_weather_tool, handle_job_search_tool, handle_todo_tool],
            tool_choice="auto",
        )

    async def classify(self, messages: list[BaseMessage]) -> dict:
        response = await self._llm.ainvoke(messages=messages)

        if not response.tool_calls:
            self._logger.info("[classify] text response")
            return {
                "messages": [AIMessage(content=response.content)],
                "current_branch": None,
            }

        # noinspection PyTypeChecker
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        branch = _TOOL_NAME_TO_BRANCH[tool_name]
        self._logger.info("[classify] tool=%s branch=%s", tool_name, branch)

        return {"current_branch": branch}
