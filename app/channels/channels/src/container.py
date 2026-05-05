from agent_v2.agent.container import AgentV2Container
from channels.common.src.container import ChannelsCommonContainer
from channels.telegram.src.container import TelegramChannelContainer
from dependency_injector import containers, providers
from utils.utils.src.container import UtilsContainer


class ChannelsContainer(containers.DeclarativeContainer):
    utils_container: UtilsContainer = providers.DependenciesContainer()
    agent_container: AgentV2Container = providers.DependenciesContainer()

    channels_common_container = providers.Container(
        ChannelsCommonContainer, utils_container=utils_container
    )

    telegram_channel_container = providers.Container(
        TelegramChannelContainer,
        agent_container=agent_container,
        channels_common_container=channels_common_container,
    )
