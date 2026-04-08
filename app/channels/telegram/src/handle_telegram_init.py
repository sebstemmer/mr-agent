from channels.common.src.save_or_update_chat_id_to_channel_type import (
    SaveOrUpdateChatIdToChannelType,
)
from channels.telegram.src.const import CHANNEL_TYPE
from telegram import Update


class HandleTelegramInit:
    def __init__(
        self,
        save_or_update_chat_id: SaveOrUpdateChatIdToChannelType,
    ):
        self._save_or_update_chat_id = save_or_update_chat_id

    async def handle(self, update: Update, _context) -> None:
        await self._save_or_update_chat_id.save_or_update(
            channel_type=CHANNEL_TYPE,
            chat_id=str(update.effective_chat.id),
        )
        await update.message.reply_text("Chat initialized, ready to go!")
