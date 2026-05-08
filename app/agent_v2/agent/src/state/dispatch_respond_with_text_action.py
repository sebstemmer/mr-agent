from logging import Logger

from langchain_core.messages import AIMessage

from agent_v2.agent.src.message_sender import MessageSender
from agent_v2.agent.src.state.agent_state import RespondWithTextAction


class DispatchRespondWithTextAction:
    def __init__(self, logger: Logger, send_message: MessageSender):
        self._logger = logger
        self._send_message = send_message

    async def dispatch(self, text: str) -> RespondWithTextAction:
        await self._send_message.send(message=text)

        return RespondWithTextAction(
            message=AIMessage(content=text),
        )
