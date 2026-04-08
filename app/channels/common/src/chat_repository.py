from channels.common.src.chat_model import Chat
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_channel_type(self, channel_type: str) -> Chat | None:
        result = await self._session.exec(
            select(Chat).where(Chat.channel_type == channel_type)
        )
        return result.first()

    async def save(self, chat: Chat) -> Chat:
        self._session.add(chat)
        await self._session.commit()
        await self._session.refresh(chat)
        return chat

    async def update(self, chat: Chat) -> Chat:
        await self._session.commit()
        await self._session.refresh(chat)
        return chat
