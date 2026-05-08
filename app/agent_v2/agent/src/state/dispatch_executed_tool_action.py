from logging import Logger

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.messages.tool import ToolCall

from agent_v2.agent.src.message_sender import MessageSender
from agent_v2.agent.src.state.agent_state import ExecutedToolAction


class DispatchExecutedToolAction:
    def __init__(self, logger: Logger, send_message: MessageSender):
        self._logger = logger
        self._send_message = send_message

    async def dispatch(
        self, call: ToolCall, tool_message: str, readable_tool_message: str
    ) -> ExecutedToolAction:
        await self._send_message.send(message=readable_tool_message)

        return ExecutedToolAction(
            tool_message=ToolMessage(content=tool_message, tool_call_id=call["id"]),
            readable_tool_message=AIMessage(content=readable_tool_message),
        )
