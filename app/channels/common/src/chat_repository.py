from channels.common.src.chat_model import Chat
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class ChatRepository:
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def find_by_channel_type(self, channel_type: str) -> Chat | None:
        async with self._session_factory() as session:
            return await self._find_by_channel_type(
                session=session, channel_type=channel_type
            )

    async def upsert_by_channel_type(self, channel_type: str, chat_id: str) -> Chat:
        async with self._session_factory() as session:
            chat = await self._find_by_channel_type(
                session=session, channel_type=channel_type
            )
            if chat is None:
                chat = Chat(channel_type=channel_type, chat_id=chat_id)
                session.add(chat)
            else:
                chat.chat_id = chat_id
            await session.commit()
            await session.refresh(chat)
            return chat

    @staticmethod
    async def _find_by_channel_type(
        session: AsyncSession, channel_type: str
    ) -> Chat | None:
        result = await session.exec(
            select(Chat).where(Chat.channel_type == channel_type)
        )
        return result.first()
