from channels.telegram.src.container import TelegramChannelContainer
from dependency_injector import containers, providers
from job_search.src.container import JobSearchContainer
from microsoft_todo.src.container import MicrosoftTodoContainer
from utils.common.src.config import settings
from weather.src.container import WeatherContainer

from scheduled_jobs.morning_briefing.src.run_morning_briefing import RunMorningBriefing


class MorningBriefingContainer(containers.DeclarativeContainer):
    job_search_container: JobSearchContainer = providers.DependenciesContainer()
    weather_container: WeatherContainer = providers.DependenciesContainer()
    microsoft_todo_container: MicrosoftTodoContainer = providers.DependenciesContainer()
    telegram_channel_container: TelegramChannelContainer = (
        providers.DependenciesContainer()
    )

    run_morning_briefing = providers.Singleton(
        RunMorningBriefing,
        greeting=settings.MORNING_BRIEFING_GREETING,
        weather_location=settings.MORNING_BRIEFING_WEATHER_LOCATION,
        refresh_jobs=job_search_container.refresh_jobs,
        get_interesting_jobs=job_search_container.get_interesting_jobs,
        get_weather=weather_container.get_weather,
        todo_client=microsoft_todo_container.microsoft_todo_client,
        send_telegram_message=telegram_channel_container.send_telegram_message,
    )
