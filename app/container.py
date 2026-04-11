from agent.agent.src.container import AgentContainer
from channels.channels.src.container import ChannelsContainer
from dependency_injector import containers, providers
from job_search.src.container import JobSearchContainer
from scheduled_jobs.morning_briefing.src.container import MorningBriefingContainer
from utils.utils.src.container import UtilsContainer
from weather.src.container import WeatherContainer


class Container(containers.DeclarativeContainer):
    utils_container = providers.Container(UtilsContainer)

    weather_container = providers.Container(
        WeatherContainer, utils_container=utils_container
    )

    job_search_container = providers.Container(
        JobSearchContainer, utils_container=utils_container
    )

    agent_container = providers.Container(
        AgentContainer,
        weather_container=weather_container,
        job_search_container=job_search_container,
    )

    channels_container = providers.Container(
        ChannelsContainer,
        utils_container=utils_container,
        agent_container=agent_container,
    )

    morning_briefing = providers.Container(
        MorningBriefingContainer,
        job_search_container=job_search_container,
        telegram_channel_container=channels_container.telegram_channel_container,
    )
