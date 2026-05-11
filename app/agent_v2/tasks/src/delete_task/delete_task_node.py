from logging import Logger

from langchain_core.messages import ToolMessage
from utils.common.src.confirm import confirm

from agent_v2.agent.src.state.agent_state import AgentState, ExecuteToolCallState
from agent_v2.agent.src.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)
from agent_v2.agent.src.state.unexpected_state_error import UnexpectedStateError
from agent_v2.tasks.src.delete_task.delete_task_tool import DeleteTaskInput, DeleteTaskTool


class DeleteTaskNode:
    def __init__(
        self,
        delete_task_tool: DeleteTaskTool,
        dispatch_executed_tool_action: DispatchExecutedToolAction,
        logger: Logger,
    ):
        self._delete_task_tool = delete_task_tool
        self._dispatch_executed_tool_action = dispatch_executed_tool_action
        self._logger = logger

    async def delete(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        if not isinstance(state, ExecuteToolCallState):
            raise UnexpectedStateError(expected=ExecuteToolCallState, actual=state)

        args = DeleteTaskInput(**state.call["args"])

        if not confirm(question=f"Delete task '{args.title}'?"):
            return {
                "state": await self._dispatch_executed_tool_action.dispatch(
                    call=state.call,
                    tool_message=f"User declined deletion of task {args.task_id}.",
                    readable_tool_message=f"Deletion of '{args.title}' declined.",
                ),
            }

        result = await self._delete_task_tool.ainvoke(input=state.call)

        return {
            "state": await self._dispatch_executed_tool_action.dispatch(
                call=state.call,
                tool_message=result.content,
                readable_tool_message=result.artifact,
            ),
        }
