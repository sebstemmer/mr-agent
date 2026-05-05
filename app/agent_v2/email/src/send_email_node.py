from logging import Logger

from langchain_core.messages import ToolMessage

from agent_v2.agent.agent_state import (
    AgentState,
    ExecutedToolAction,
    ExecuteToolCallState,
)
from agent_v2.email.src.send_email_tool import SendEmailTool


class SendEmailNode:
    def __init__(
        self,
        send_email_tool: SendEmailTool,
        logger: Logger,
    ):
        self._send_email_tool = send_email_tool
        self._logger = logger

    async def send(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        if not isinstance(state, ExecuteToolCallState):
            raise ValueError(
                f"Expected ExecuteToolCallState, got {type(state).__name__}"
            )

        result = await self._send_email_tool.ainvoke(input=state.call)

        return {
            "state": ExecutedToolAction(
                message=ToolMessage(
                    content=result.content, tool_call_id=state.call["id"]
                ),
                displayable_message=result.artifact,
            ),
        }
