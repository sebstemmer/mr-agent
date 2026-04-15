from logging import Logger
from typing import Type

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from utils.common.src.llm_with_system_prompt import LlmWithSystemPrompt
from utils.common.src.sync_run_not_implemented import SyncRunNotImplemented
from utils.common.src.unknown_tool_called import UnknownToolCalled

from agent.microsoft_todo.src.create_task_tool import CreateTaskTool

TODO_BRANCH = "todo"
_LEAVE_TODO_BRANCH_TOOL_NAME = "leave_todo_branch"


class _LeaveInput(BaseModel):
    pass


class _LeaveTodoBranchTool(BaseTool):
    name: str = _LEAVE_TODO_BRANCH_TOOL_NAME
    description: str = (
        "Use when the user has changed topic and is no longer asking about todos."
    )
    args_schema: Type[BaseModel] = _LeaveInput

    async def _arun(self) -> None:
        pass

    def _run(self) -> None:
        raise SyncRunNotImplemented()


class HandleTodoNode:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        create_task_tool: CreateTaskTool,
        logger: Logger,
    ):
        self._create_task_tool = create_task_tool
        self._logger = logger
        self._llm = LlmWithSystemPrompt(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            tools=[
                create_task_tool,
                _LeaveTodoBranchTool(),
            ],
            tool_choice="auto",
        )

    async def handle(self, messages: list[BaseMessage]) -> dict:
        self._logger.info("[branch=%s] handling", TODO_BRANCH)
        response = await self._llm.ainvoke(messages=messages)

        if not response.tool_calls:
            self._logger.info("[branch=%s] text response", TODO_BRANCH)
            return {
                "messages": [AIMessage(content=response.content)],
                "current_branch": TODO_BRANCH,
            }

        # noinspection PyTypeChecker
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        self._logger.info("[branch=%s] tool=%s", TODO_BRANCH, tool_name)

        if tool_name == _LEAVE_TODO_BRANCH_TOOL_NAME:
            return {"current_branch": None}

        if tool_name == self._create_task_tool.name:
            result = await self._create_task_tool.ainvoke(input=tool_call["args"])
            return {
                "messages": [AIMessage(content=result)],
                "current_branch": TODO_BRANCH,
            }

        raise UnknownToolCalled(tool_name=tool_name)
