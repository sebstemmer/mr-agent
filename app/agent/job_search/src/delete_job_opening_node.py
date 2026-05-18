from logging import Logger

from langchain_core.messages import ToolMessage
from utils.common.src.confirm import confirm

from agent.agent.src.invoke_tool import invoke_tool
from agent.agent.src.state.agent_state import AgentState, ExecuteToolCallState
from agent.agent.src.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)
from agent.agent.src.state.unexpected_state_error import UnexpectedStateError
from agent.job_search.src.delete_job_opening_tool import (
    DeleteJobOpeningInput,
    DeleteJobOpeningTool,
)


class DeleteJobOpeningNode:
    def __init__(
        self,
        delete_job_opening_tool: DeleteJobOpeningTool,
        dispatch_executed_tool_action: DispatchExecutedToolAction,
        logger: Logger,
    ):
        self._delete_job_opening_tool = delete_job_opening_tool
        self._dispatch_executed_tool_action = dispatch_executed_tool_action
        self._logger = logger

    async def delete(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        if not isinstance(state, ExecuteToolCallState):
            raise UnexpectedStateError(expected=ExecuteToolCallState, actual=state)

        args = DeleteJobOpeningInput(**state.call["args"])

        if not confirm(question=f"Delete job opening '{args.title}'?"):
            return {
                "state": await self._dispatch_executed_tool_action.dispatch(
                    tool_message=ToolMessage(
                        content=f"User declined deletion of job opening {args.uuid}.",
                        tool_call_id=state.call["id"],
                    ),
                    readable_tool_message=f"Deletion of '{args.title}' declined.",
                ),
            }

        return {
            "state": await invoke_tool(
                tool=self._delete_job_opening_tool,
                call=state.call,
                dispatch_executed_tool_action=self._dispatch_executed_tool_action,
                error_message="Failed to delete job opening.",
                logger=self._logger,
            ),
        }
