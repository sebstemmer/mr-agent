from channels.common.src.chat_model import Chat
from channels.common.src.chat_repository import ChatRepository


class SaveOrUpdateChatIdToChannelType:
    def __init__(self, chat_repo: ChatRepository):
        self._chat_repo = chat_repo

    async def save_or_update(self, channel_type: str, chat_id: str) -> Chat:
        return await self._chat_repo.upsert_by_channel_type(
            channel_type=channel_type, chat_id=chat_id
        )
