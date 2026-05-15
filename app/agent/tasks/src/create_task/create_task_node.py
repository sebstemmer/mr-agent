from logging import Logger

from agent.agent.src.invoke_tool import invoke_tool
from agent.agent.src.state.agent_state import AgentState, ExecuteToolCallState
from agent.agent.src.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)
from agent.agent.src.state.unexpected_state_error import UnexpectedStateError
from agent.tasks.src.create_task.create_task_tool import CreateTaskTool


class CreateTaskNode:
    def __init__(
        self,
        create_task_tool: CreateTaskTool,
        dispatch_executed_tool_action: DispatchExecutedToolAction,
        logger: Logger,
    ):
        self._create_task_tool = create_task_tool
        self._dispatch_executed_tool_action = dispatch_executed_tool_action
        self._logger = logger

    async def create(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        if not isinstance(state, ExecuteToolCallState):
            raise UnexpectedStateError(expected=ExecuteToolCallState, actual=state)

        return {
            "state": await invoke_tool(
                tool=self._create_task_tool,
                call=state.call,
                dispatch_executed_tool_action=self._dispatch_executed_tool_action,
                error_message="Failed to create task.",
                logger=self._logger,
            ),
        }
