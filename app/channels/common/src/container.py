from channels.common.src.chat_repository import ChatRepository
from channels.common.src.save_or_update_chat_id_to_channel_type import (
    SaveOrUpdateChatIdToChannelType,
)
from dependency_injector import containers, providers
from sqlmodel.ext.asyncio.session import AsyncSession


class ChannelsCommonContainer(containers.DeclarativeContainer):
    session = providers.Dependency(instance_of=AsyncSession)

    chat_repo = providers.Singleton(ChatRepository, session=session)
    save_or_update_chat_id_to_channel_type = providers.Singleton(
        SaveOrUpdateChatIdToChannelType,
        chat_repo=chat_repo,
    )
