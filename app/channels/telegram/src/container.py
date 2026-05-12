from channels.common.src.container import ChannelsCommonContainer
from channels.telegram.src.bot import TelegramBot
from channels.telegram.src.handle_telegram_init import HandleTelegramInit
from channels.telegram.src.send_telegram_message import SendTelegramMessage
from dependency_injector import containers, providers
from utils.common.src.config import settings


class TelegramChannelContainer(containers.DeclarativeContainer):
    channels_common_container: ChannelsCommonContainer = (
        providers.DependenciesContainer()
    )

    handle_init = providers.Singleton(
        HandleTelegramInit,
        save_or_update_chat_id=channels_common_container.save_or_update_chat_id_to_channel_type,
    )

    bot = providers.Singleton(
        TelegramBot, token=settings.TELEGRAM_BOT_TOKEN, handle_init=handle_init
    )

    send_telegram_message = providers.Singleton(
        SendTelegramMessage,
        bot=bot,
        chat_repo=channels_common_container.chat_repo,
    )
