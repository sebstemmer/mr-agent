from logging import Logger

from agent.agent.src.invoke_tool import invoke_tool
from agent.agent.src.state.agent_state import AgentState, ExecuteToolCallState
from agent.agent.src.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)
from agent.agent.src.state.unexpected_state_error import UnexpectedStateError
from agent.job_search.src.create_job_opening_tool import CreateJobOpeningTool
from files.src.delete_file import DeleteFile


class CreateJobOpeningNode:
    def __init__(
        self,
        create_job_opening_tool: CreateJobOpeningTool,
        dispatch_executed_tool_action: DispatchExecutedToolAction,
        delete_file: DeleteFile,
        logger: Logger,
    ):
        self._create_job_opening_tool = create_job_opening_tool
        self._dispatch_executed_tool_action = dispatch_executed_tool_action
        self._delete_file = delete_file
        self._logger = logger

    async def create(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        if not isinstance(state, ExecuteToolCallState):
            raise UnexpectedStateError(expected=ExecuteToolCallState, actual=state)

        file_uuid = state.call["args"].get("file_uuid")

        return {
            "state": await invoke_tool(
                tool=self._create_job_opening_tool,
                call=state.call,
                dispatch_executed_tool_action=self._dispatch_executed_tool_action,
                error_message="Failed to create job opening.",
                logger=self._logger,
                on_error=lambda: self._delete_file.delete(uuid=file_uuid) if file_uuid else None,
            ),
        }
