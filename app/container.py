from agent.src.container import AgentContainer
from channels.common.src.container import ChannelsCommonContainer
from channels.telegram.src.container import TelegramContainer
from conversation.src.container import ConversationContainer
from dependency_injector import containers, providers
from job_search.src.container import JobSearchContainer
from scheduled_jobs.morning_briefing.src.container import MorningBriefingContainer
from utils.src.config import settings
from utils.src.container import UtilsContainer
from weather.src.container import WeatherContainer


class Container(containers.DeclarativeContainer):
    utils = providers.Container(UtilsContainer)

    job_search = providers.Container(
        JobSearchContainer,
        session=utils.container.session,
        http_client=utils.container.http_client,
    )

    conversation = providers.Container(ConversationContainer)

    weather = providers.Container(
        WeatherContainer,
        http_client=utils.container.http_client,
    )

    agent_container = providers.Container(
        AgentContainer,
        handle_conversation=conversation.container.handle_conversation,
        handle_conversation_tool=conversation.container.handle_conversation_tool,
        handle_weather=weather.container.handle_weather,
        handle_weather_tool=weather.container.handle_weather_tool,
        handle_job_search=job_search.container.handle_job_search,
        handle_job_search_tool=job_search.container.handle_job_search_tool,
    )

    channels_common = providers.Container(
        ChannelsCommonContainer,
        session=utils.container.session,
    )

    telegram = providers.Container(
        TelegramContainer,
        chat_repo=channels_common.container.chat_repo,
        save_or_update_chat_id=channels_common.container.save_or_update_chat_id_to_channel_type,
        agent=agent_container.container.agent,
        telegram_bot_token=providers.Object(settings.TELEGRAM_BOT_TOKEN),
    )

    morning_briefing = providers.Container(
        MorningBriefingContainer,
        refresh_jobs=job_search.container.refreshJobs,
        job_repo=job_search.container.job_repo,
        send_telegram_message=telegram.container.send_telegram_message,
    )
