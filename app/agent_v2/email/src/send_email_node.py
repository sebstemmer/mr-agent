from logging import Logger

from agent_v2.agent.state.agent_state import AgentState, ExecuteToolCallState
from agent_v2.agent.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)
from agent_v2.agent.state.unexpected_state_error import UnexpectedStateError
from agent_v2.email.src.send_email_tool import SendEmailTool


class SendEmailNode:
    def __init__(
        self,
        send_email_tool: SendEmailTool,
        dispatch_executed_tool_action: DispatchExecutedToolAction,
        logger: Logger,
    ):
        self._send_email_tool = send_email_tool
        self._dispatch_executed_tool_action = dispatch_executed_tool_action
        self._logger = logger

    async def send(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        if not isinstance(state, ExecuteToolCallState):
            raise UnexpectedStateError(expected=ExecuteToolCallState, actual=state)

        result = await self._send_email_tool.ainvoke(input=state.call)

        return {
            "state": await self._dispatch_executed_tool_action.dispatch(
                call=state.call,
                tool_message=result.content,
                readable_tool_message=result.artifact,
            ),
        }
