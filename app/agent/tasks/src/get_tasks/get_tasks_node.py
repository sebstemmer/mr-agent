from logging import Logger

from agent.agent.src.invoke_tool import invoke_tool
from agent.agent.src.state.agent_state import AgentState, ExecuteToolCallState
from agent.agent.src.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)
from agent.agent.src.state.unexpected_state_error import UnexpectedStateError
from agent.tasks.src.get_tasks.get_tasks_tool import GetTasksTool


class GetTasksNode:
    def __init__(
        self,
        get_tasks_tool: GetTasksTool,
        dispatch_executed_tool_action: DispatchExecutedToolAction,
        logger: Logger,
    ):
        self._get_tasks_tool = get_tasks_tool
        self._dispatch_executed_tool_action = dispatch_executed_tool_action
        self._logger = logger

    async def get(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        if not isinstance(state, ExecuteToolCallState):
            raise UnexpectedStateError(expected=ExecuteToolCallState, actual=state)

        return {
            "state": await invoke_tool(
                tool=self._get_tasks_tool,
                call=state.call,
                dispatch_executed_tool_action=self._dispatch_executed_tool_action,
                error_message="Failed to get tasks.",
                logger=self._logger,
            ),
        }
