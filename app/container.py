from agent.agent.src.container import AgentContainer
from channels.channels.src.container import ChannelsContainer
from dependency_injector import containers, providers
from files.src.container import FilesContainer
from job_search.src.container import JobSearchContainer
from microsoft_todo.src.container import MicrosoftTodoContainer
from scheduled_jobs.morning_briefing.src.container import MorningBriefingContainer
from utils.common.src.config import settings
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

    microsoft_todo_container = providers.Container(
        MicrosoftTodoContainer, utils_container=utils_container
    )

    files_container = providers.Container(
        FilesContainer,
        utils_container=utils_container,
        base_dir=settings.FILE_STORAGE_DIR,
    )

    channels_container = providers.Container(
        ChannelsContainer,
        utils_container=utils_container,
        files_container=files_container,
    )

    agent_container = providers.Container(
        AgentContainer,
        weather_container=weather_container,
        microsoft_todo_container=microsoft_todo_container,
        job_search_container=job_search_container,
        files_container=files_container,
        send_message=channels_container.telegram_channel_container.send_telegram_message,
    )

    morning_briefing = providers.Container(
        MorningBriefingContainer,
        job_search_container=job_search_container,
        weather_container=weather_container,
        microsoft_todo_container=microsoft_todo_container,
        telegram_channel_container=channels_container.telegram_channel_container,
    )
