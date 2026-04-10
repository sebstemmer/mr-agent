from channels.telegram.src.container import TelegramChannelContainer
from dependency_injector import containers, providers
from job_search.src.container import JobSearchContainer

from scheduled_jobs.morning_briefing.src.run_morning_briefing import RunMorningBriefing


class MorningBriefingContainer(containers.DeclarativeContainer):
    job_search_container: JobSearchContainer = providers.DependenciesContainer()
    telegram_channel_container: TelegramChannelContainer = (
        providers.DependenciesContainer()
    )

    run_morning_briefing = providers.Singleton(
        RunMorningBriefing,
        refresh_jobs=job_search_container.refresh_jobs,
        job_repo=job_search_container.job_repo,
        send_telegram_message=telegram_channel_container.send_telegram_message,
    )
