from logging import Logger

from langchain_core.messages import ToolMessage
from utils.common.src.confirm import confirm

from agent_v2.agent.src.invoke_tool import invoke_tool
from agent_v2.agent.src.state.agent_state import AgentState, ExecuteToolCallState
from agent_v2.agent.src.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)
from agent_v2.agent.src.state.unexpected_state_error import UnexpectedStateError
from agent_v2.job_search.src.like_job_tool import LikeJobInput, LikeJobTool


class LikeJobNode:
    def __init__(
        self,
        like_job_tool: LikeJobTool,
        dispatch_executed_tool_action: DispatchExecutedToolAction,
        logger: Logger,
    ):
        self._like_job_tool = like_job_tool
        self._dispatch_executed_tool_action = dispatch_executed_tool_action
        self._logger = logger

    async def like(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        if not isinstance(state, ExecuteToolCallState):
            raise UnexpectedStateError(expected=ExecuteToolCallState, actual=state)

        args = LikeJobInput(**state.call["args"])

        if not confirm(question=f"Like job {args.public_id}?"):
            return {
                "state": await self._dispatch_executed_tool_action.dispatch(
                    tool_message=ToolMessage(
                        content=f"User declined liking job {args.public_id}.",
                        tool_call_id=state.call["id"],
                    ),
                    readable_tool_message=f"Skipped liking job {args.public_id}.",
                ),
            }

        return {
            "state": await invoke_tool(
                tool=self._like_job_tool,
                call=state.call,
                dispatch_executed_tool_action=self._dispatch_executed_tool_action,
                error_message="Failed to like job.",
            ),
        }
