from agent.agent.src.container import AgentContainer
from channels.common.src.container import ChannelsCommonContainer
from channels.telegram.src.container import TelegramChannelContainer
from dependency_injector import containers, providers
from job_search.src.container import JobSearchContainer
from utils.src.container import UtilsContainer
from weather.src.container import WeatherContainer


class ChannelsContainer(containers.DeclarativeContainer):
    utils_container: UtilsContainer = providers.DependenciesContainer()
    weather_container: WeatherContainer = providers.DependenciesContainer()
    job_search_container: JobSearchContainer = providers.DependenciesContainer()
    agent_container: AgentContainer = providers.DependenciesContainer()

    channels_common_container = providers.Container(
        ChannelsCommonContainer, utils_container=utils_container
    )

    telegram_channel_container = providers.Container(
        TelegramChannelContainer,
        utils_container=utils_container,
        job_search_container=job_search_container,
        agent_container=agent_container,
        channels_common_container=channels_common_container,
    )
