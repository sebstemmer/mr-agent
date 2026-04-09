from logging import Logger
from typing import Type

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from utils.src.sync_run_not_implemented import SyncRunNotImplemented
from utils.src.unknown_tool_called import UnknownToolCalled

from job_search.src.get_jobs_tool import GetJobsTool
from job_search.src.job_search_status_tool import JobSearchStatusTool

JOB_SEARCH_BRANCH = "job_search"
LEAVE_JOB_SEARCH_BRANCH_TOOL_NAME = "leave_job_search_branch"


class _LeaveInput(BaseModel):
    pass


class _LeaveJobSearchBranchTool(BaseTool):
    name: str = LEAVE_JOB_SEARCH_BRANCH_TOOL_NAME
    description: str = (
        "Use when the user has changed topic and is no longer asking about job search."
    )
    args_schema: Type[BaseModel] = _LeaveInput

    async def _arun(self) -> None:
        pass

    def _run(self) -> None:
        raise SyncRunNotImplemented()


class HandleJobSearchNode:
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

        # noinspection PyTypeChecker
        llm = ChatOpenAI(api_key=api_key, model=model)
        self._llm = llm.bind_tools(
            [get_jobs_tool, job_search_status_tool, _LeaveJobSearchBranchTool()],
            tool_choice="auto",
        )

    async def handle(self, messages: list[BaseMessage]) -> dict:
        self._logger.info("[branch=%s] handling", JOB_SEARCH_BRANCH)
        response = await self._llm.ainvoke(messages)

        if not response.tool_calls:
            self._logger.info("[branch=%s] text response", JOB_SEARCH_BRANCH)
            return {
                "messages": [AIMessage(content=response.content)],
                "current_branch": JOB_SEARCH_BRANCH,
            }

        # noinspection PyTypeChecker
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        self._logger.info("[branch=%s] tool=%s", JOB_SEARCH_BRANCH, tool_name)

        if tool_name == LEAVE_JOB_SEARCH_BRANCH_TOOL_NAME:
            return {"current_branch": None}

        if tool_name == self._get_jobs_tool.name:
            result = await self._get_jobs_tool.ainvoke(input=tool_call["args"])
            return {
                "messages": [AIMessage(content=result)],
                "current_branch": JOB_SEARCH_BRANCH,
            }

        if tool_name == self._job_search_status_tool.name:
            result = await self._job_search_status_tool.ainvoke(input=tool_call["args"])
            return {
                "messages": [AIMessage(content=result)],
                "current_branch": JOB_SEARCH_BRANCH,
            }

        raise UnknownToolCalled(tool_name=tool_name)
