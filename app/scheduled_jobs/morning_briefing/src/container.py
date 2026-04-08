from channels.telegram.src.send_telegram_message import SendTelegramMessage
from dependency_injector import containers, providers
from job_search.src.job_repository import JobRepository
from job_search.src.refresh_jobs import RefreshJobs
from scheduled_jobs.morning_briefing.src.run_morning_briefing import RunMorningBriefing


class MorningBriefingContainer(containers.DeclarativeContainer):
    refresh_jobs = providers.Dependency(instance_of=RefreshJobs)
    job_repo = providers.Dependency(instance_of=JobRepository)
    send_telegram_message = providers.Dependency(instance_of=SendTelegramMessage)

    run_morning_briefing = providers.Singleton(
        RunMorningBriefing,
        refresh_jobs=refresh_jobs,
        job_repo=job_repo,
        send_telegram_message=send_telegram_message,
    )
