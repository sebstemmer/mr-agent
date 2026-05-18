from logging import Logger

from agent.agent.src.invoke_tool import invoke_tool
from agent.agent.src.state.agent_state import AgentState, ExecuteToolCallState
from agent.agent.src.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)
from agent.agent.src.state.unexpected_state_error import UnexpectedStateError
from agent.job_search.src.apply_job_opening_tool import ApplyJobOpeningTool


class ApplyJobOpeningNode:
    def __init__(
        self,
        apply_job_opening_tool: ApplyJobOpeningTool,
        dispatch_executed_tool_action: DispatchExecutedToolAction,
        logger: Logger,
    ):
        self._apply_job_opening_tool = apply_job_opening_tool
        self._dispatch_executed_tool_action = dispatch_executed_tool_action
        self._logger = logger

    async def apply(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        if not isinstance(state, ExecuteToolCallState):
            raise UnexpectedStateError(expected=ExecuteToolCallState, actual=state)

        return {
            "state": await invoke_tool(
                tool=self._apply_job_opening_tool,
                call=state.call,
                dispatch_executed_tool_action=self._dispatch_executed_tool_action,
                error_message="Failed to apply for job opening.",
                logger=self._logger,
            ),
        }
