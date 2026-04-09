from logging import Logger
from typing import Type

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from utils.src.sync_run_not_implemented import SyncRunNotImplemented

from job_search.src.get_jobs_tool import GetJobsTool
from job_search.src.job_search_status_tool import JobSearchStatusTool

JOB_SEARCH_BRANCH = "job_search"

_SYSTEM_PROMPT = (
    "You are in the job search branch. You must call exactly one tool.\n\n"
    "Rules:\n"
    "- Call get_jobs only when the user has provided a date range. "
    "If the user asks for jobs without specifying when, call stay_in_job_search_branch "
    "to ask them for the date range.\n"
    "- Call job_search_status only when the user explicitly asks when jobs were last "
    "fetched or about the search status. Never use it as a fallback.\n"
    "- Call stay_in_job_search_branch when the user is still talking about job search "
    "but you need more information before calling another tool.\n"
    "- Call leave_job_search_branch when the user has changed topic and is no longer "
    "asking about job search."
)


class _ResponseInput(BaseModel):
    response: str = Field(description="The response to send to the user")


class _StayInJobSearchBranchTool(BaseTool):
    name: str = "stay_in_job_search_branch"
    description: str = (
        "Use when the user is still in the context of job search but no other "
        "job search tool should be called. For example, asking the user for "
        "missing information needed to call a tool."
    )
    args_schema: Type[BaseModel] = _ResponseInput

    async def _arun(self, response: str) -> str:
        return response

    def _run(self, response: str) -> str:
        raise SyncRunNotImplemented()


class _LeaveJobSearchBranchTool(BaseTool):
    name: str = "leave_job_search_branch"
    description: str = (
        "Use when the user has changed topic and is no longer asking about job search."
    )
    args_schema: Type[BaseModel] = _ResponseInput

    async def _arun(self, response: str) -> str:
        return response

    def _run(self, response: str) -> str:
        raise SyncRunNotImplemented()


class HandleJobSearch:
    def __init__(
        self,
        api_key: str,
        model: str,
        get_jobs_tool: GetJobsTool,
        job_search_status_tool: JobSearchStatusTool,
        logger: Logger,
    ):
        self._get_jobs_tool = get_jobs_tool
        self._job_search_status_tool = job_search_status_tool
        self._logger = logger
        self._stay_tool = _StayInJobSearchBranchTool()
        self._leave_tool = _LeaveJobSearchBranchTool()

        # noinspection PyTypeChecker
        llm = ChatOpenAI(api_key=api_key, model=model)

        self._llm = llm.bind_tools(
            [get_jobs_tool, job_search_status_tool, self._stay_tool, self._leave_tool],
            tool_choice="required",
        )

    async def handle(self, messages: list[BaseMessage]) -> dict:
        self._logger.info("[branch=%s] handling", JOB_SEARCH_BRANCH)
        response = await self._llm.ainvoke([SystemMessage(content=_SYSTEM_PROMPT)] + messages)

        # noinspection PyTypeChecker
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        self._logger.info("[branch=%s] tool=%s", JOB_SEARCH_BRANCH, tool_name)

        if tool_name == "get_jobs":
            result = await self._get_jobs_tool.ainvoke(input=tool_call["args"])
            return {"messages": [AIMessage(content=result)], "current_branch": JOB_SEARCH_BRANCH}

        if tool_name == "job_search_status":
            result = await self._job_search_status_tool.ainvoke(input=tool_call["args"])
            return {"messages": [AIMessage(content=result)], "current_branch": JOB_SEARCH_BRANCH}

        if tool_name == "stay_in_job_search_branch":
            return {
                "messages": [AIMessage(content=tool_call["args"]["response"])],
                "current_branch": JOB_SEARCH_BRANCH,
            }

        return {"current_branch": None}
