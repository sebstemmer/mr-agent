from logging import Logger

from langchain_core.messages import AIMessage, ToolMessage

from agent.agent.src.message_sender import MessageSender
from agent.agent.src.state.agent_state import ExecutedToolAction


class DispatchExecutedToolAction:
    def __init__(self, logger: Logger, send_message: MessageSender):
        self._logger = logger
        self._send_message = send_message

    async def dispatch(
        self, tool_message: ToolMessage, readable_tool_message: str
    ) -> ExecutedToolAction:
        await self._send_message.send(message=readable_tool_message)

        return ExecutedToolAction(
            tool_message=tool_message,
            readable_tool_message=AIMessage(content=readable_tool_message),
        )
