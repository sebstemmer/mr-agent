import logging

from channels.common.src.chat_repository import ChatRepository
from channels.common.src.split_message import split_message
from channels.telegram.src.bot import TelegramBot
from channels.telegram.src.const import CHANNEL_TYPE

_logger = logging.getLogger(__name__)


class SendTelegramMessage:
    def __init__(self, bot: TelegramBot, chat_repo: ChatRepository):
        self._bot = bot
        self._chat_repo = chat_repo

    async def send(self, message: str) -> None:
        chat = await self._chat_repo.find_by_channel_type(channel_type=CHANNEL_TYPE)
        if not chat:
            _logger.info("No telegram chat_id stored yet, skipping message")
            return
        for part in split_message(text=message, max_length=4096):
            await self._bot.app.bot.send_message(
                chat_id=chat.chat_id,
                text=part,
                parse_mode="Markdown",
            )
