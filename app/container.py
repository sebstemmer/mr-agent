from channels.common.src.container import ChannelsCommonContainer
from channels.telegram.src.container import TelegramContainer
from dependency_injector import containers, providers
from job_search.src.container import JobSearchContainer
from job_search.src.get_jobs_tool import GetJobsTool
from job_search.src.job_search_status_tool import JobSearchStatusTool
from langgraph.graph.state import CompiledStateGraph
from scheduled_jobs.morning_briefing.src.container import MorningBriefingContainer
from utils.src.config import settings
from utils.src.container import UtilsContainer


class Container(containers.DeclarativeContainer):
    utils = providers.Container(UtilsContainer)

    job_search = providers.Container(
        JobSearchContainer,
        session=utils.container.session,
        http_client=utils.container.http_client,
    )

    get_jobs_tool = providers.Singleton(
        GetJobsTool,
        job_repo=job_search.container.job_repo,
        refresh_jobs=job_search.container.refreshJobs,
    )

    job_search_status_tool = providers.Singleton(
        JobSearchStatusTool,
        state_repo=job_search.container.state_repo,
    )

    channels_common = providers.Container(
        ChannelsCommonContainer,
        session=utils.container.session,
    )

    agent = providers.Dependency(instance_of=CompiledStateGraph)

    telegram = providers.Container(
        TelegramContainer,
        chat_repo=channels_common.container.chat_repo,
        save_or_update_chat_id=channels_common.container.save_or_update_chat_id_to_channel_type,
        agent=agent,
        telegram_bot_token=providers.Object(settings.TELEGRAM_BOT_TOKEN),
    )

    morning_briefing = providers.Container(
        MorningBriefingContainer,
        refresh_jobs=job_search.container.refreshJobs,
        job_repo=job_search.container.job_repo,
        send_telegram_message=telegram.container.send_telegram_message,
    )
