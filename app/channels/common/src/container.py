from channels.common.src.chat_repository import ChatRepository
from channels.common.src.save_or_update_chat_id_to_channel_type import (
    SaveOrUpdateChatIdToChannelType,
)
from dependency_injector import containers, providers
from utils.src.container import UtilsContainer


class ChannelsCommonContainer(containers.DeclarativeContainer):
    utils_container: UtilsContainer = providers.DependenciesContainer()

    chat_repo = providers.Singleton(ChatRepository, session=utils_container.session)
    save_or_update_chat_id_to_channel_type = providers.Singleton(
        SaveOrUpdateChatIdToChannelType,
        chat_repo=chat_repo,
    )
