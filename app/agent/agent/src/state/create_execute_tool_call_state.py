from logging import Logger

from langchain_core.messages.tool import ToolCall

from agent.agent.src.message_sender import MessageSender
from agent.agent.src.state.agent_state import ExecuteToolCallState
from agent.agent.src.tool_registry import ToolRegistry


class CreateExecuteToolCallState:
    def __init__(
        self,
        logger: Logger,
        send_message: MessageSender,
        tool_registry: ToolRegistry,
    ):
        self._logger = logger
        self._send_message = send_message
        self._tool_registry = tool_registry

    async def create(self, call: ToolCall) -> ExecuteToolCallState:
        display_name = self._tool_registry[call["name"]].display_name

        await self._send_message.send(message=f"Calling the {display_name}...")

        return ExecuteToolCallState(messages=[], call=call)
