from logging import Logger

from langchain_core.messages import AIMessage, BaseMessage
from utils.common.src.llm_with_system_prompt import LlmWithSystemPrompt
from utils.common.src.unknown_tool_called import UnknownToolCalled

from agent.job_search.src.get_jobs_tool import GetJobsTool
from agent.job_search.src.job_search_status_tool import JobSearchStatusTool
from agent.job_search.src.like_job_tool import LikeJobTool

JOB_SEARCH_BRANCH = "job_search"


class HandleJobSearchNode:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        get_jobs_tool: GetJobsTool,
        job_search_status_tool: JobSearchStatusTool,
        like_job_tool: LikeJobTool,
        logger: Logger,
    ):
        self._get_jobs_tool = get_jobs_tool
        self._job_search_status_tool = job_search_status_tool
        self._like_job_tool = like_job_tool
        self._logger = logger
        self._llm = LlmWithSystemPrompt(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            tools=[
                get_jobs_tool,
                job_search_status_tool,
                like_job_tool,
            ],
            tool_choice="auto",
            parallel_tool_calls=False,
            additional_instructions=[
                "You are only responsible for job search-related requests."
                " Ignore anything unrelated to job search."
            ],
        )

    async def handle(self, messages: list[BaseMessage]) -> dict:
        self._logger.info("[branch=%s] handling", JOB_SEARCH_BRANCH)
        response = await self._llm.ainvoke(messages=messages)

        if not response.tool_calls:
            self._logger.info("[branch=%s] text response", JOB_SEARCH_BRANCH)
            return {"messages": [AIMessage(content=response.content)]}

        # noinspection PyTypeChecker
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        self._logger.info("[branch=%s] tool=%s", JOB_SEARCH_BRANCH, tool_name)

        if tool_name == self._get_jobs_tool.name:
            result = await self._get_jobs_tool.ainvoke(input=tool_call["args"])
            return {"messages": [AIMessage(content=result)]}

        if tool_name == self._job_search_status_tool.name:
            result = await self._job_search_status_tool.ainvoke(input=tool_call["args"])
            return {"messages": [AIMessage(content=result)]}

        if tool_name == self._like_job_tool.name:
            result = await self._like_job_tool.ainvoke(input=tool_call["args"])
            return {"messages": [AIMessage(content=result)]}

        raise UnknownToolCalled(tool_name=tool_name)
