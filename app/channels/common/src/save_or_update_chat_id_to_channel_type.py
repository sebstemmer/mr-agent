from channels.common.src.chat_model import Chat
from channels.common.src.chat_repository import ChatRepository


class SaveOrUpdateChatIdToChannelType:
    def __init__(self, chat_repo: ChatRepository):
        self._chat_repo = chat_repo

    async def save_or_update(self, channel_type: str, chat_id: str) -> Chat:
        chat = await self._chat_repo.find_by_channel_type(channel_type=channel_type)
        if chat:
            chat.chat_id = chat_id
            return await self._chat_repo.update(chat=chat)
        chat = Chat(channel_type=channel_type, chat_id=chat_id)
        return await self._chat_repo.save(chat=chat)
