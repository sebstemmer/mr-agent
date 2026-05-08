from logging import Logger

from agent_v2.agent.src.state.agent_state import AgentState, ExecuteToolCallState
from agent_v2.agent.src.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)
from agent_v2.agent.src.state.unexpected_state_error import UnexpectedStateError
from agent_v2.tasks.src.get_tasks.get_tasks_tool import GetTasksTool


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

        result = await self._get_tasks_tool.ainvoke(input=state.call)

        return {
            "state": await self._dispatch_executed_tool_action.dispatch(
                call=state.call,
                tool_message=result.content,
                readable_tool_message=result.artifact,
            ),
        }
