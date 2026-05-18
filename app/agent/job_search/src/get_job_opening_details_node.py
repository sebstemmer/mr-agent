from logging import Logger

from agent.agent.src.invoke_tool import invoke_tool
from agent.agent.src.state.agent_state import AgentState, ExecuteToolCallState
from agent.agent.src.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)
from agent.agent.src.state.unexpected_state_error import UnexpectedStateError
from agent.job_search.src.get_job_opening_details_tool import GetJobOpeningDetailsTool


class GetJobOpeningDetailsNode:
    def __init__(
        self,
        get_job_opening_details_tool: GetJobOpeningDetailsTool,
        dispatch_executed_tool_action: DispatchExecutedToolAction,
        logger: Logger,
    ):
        self._get_job_opening_details_tool = get_job_opening_details_tool
        self._dispatch_executed_tool_action = dispatch_executed_tool_action
        self._logger = logger

    async def get(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        if not isinstance(state, ExecuteToolCallState):
            raise UnexpectedStateError(expected=ExecuteToolCallState, actual=state)

        return {
            "state": await invoke_tool(
                tool=self._get_job_opening_details_tool,
                call=state.call,
                dispatch_executed_tool_action=self._dispatch_executed_tool_action,
                error_message="Failed to get job opening details.",
                logger=self._logger,
            ),
        }
