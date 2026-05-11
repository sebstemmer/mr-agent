from logging import Logger

from agent_v2.agent.src.state.agent_state import AgentState, ExecuteToolCallState
from agent_v2.agent.src.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)
from agent_v2.agent.src.state.unexpected_state_error import UnexpectedStateError
from agent_v2.tasks.src.update_task.update_task_tool import UpdateTaskTool


class UpdateTaskNode:
    def __init__(
        self,
        update_task_tool: UpdateTaskTool,
        dispatch_executed_tool_action: DispatchExecutedToolAction,
        logger: Logger,
    ):
        self._update_task_tool = update_task_tool
        self._dispatch_executed_tool_action = dispatch_executed_tool_action
        self._logger = logger

    async def update(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        if not isinstance(state, ExecuteToolCallState):
            raise UnexpectedStateError(expected=ExecuteToolCallState, actual=state)

        result = await self._update_task_tool.ainvoke(input=state.call)

        return {
            "state": await self._dispatch_executed_tool_action.dispatch(
                call=state.call,
                tool_message=result.content,
                readable_tool_message=result.artifact,
            ),
        }
