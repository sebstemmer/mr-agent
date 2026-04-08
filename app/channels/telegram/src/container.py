from channels.common.src.chat_repository import ChatRepository
from channels.common.src.save_or_update_chat_id_to_channel_type import (
    SaveOrUpdateChatIdToChannelType,
)
from channels.telegram.src.bot import TelegramBot
from channels.telegram.src.handle_telegram_init import HandleTelegramInit
from channels.telegram.src.handle_telegram_message import HandleTelegramMessage
from channels.telegram.src.send_telegram_message import SendTelegramMessage
from dependency_injector import containers, providers
from langgraph.graph.state import CompiledStateGraph


class TelegramContainer(containers.DeclarativeContainer):
    chat_repo = providers.Dependency(instance_of=ChatRepository)
    save_or_update_chat_id = providers.Dependency(
        instance_of=SaveOrUpdateChatIdToChannelType,
    )
    agent = providers.Dependency(instance_of=CompiledStateGraph)
    telegram_bot_token = providers.Dependency(instance_of=str)

    handle_init = providers.Singleton(
        HandleTelegramInit,
        save_or_update_chat_id=save_or_update_chat_id,
    )

    handle_message = providers.Singleton(
        HandleTelegramMessage,
        agent=agent,
        save_or_update_chat_id=save_or_update_chat_id,
    )

    bot = providers.Singleton(
        TelegramBot,
        token=telegram_bot_token,
        handle_init=handle_init,
        handle_message=handle_message,
    )

    send_telegram_message = providers.Singleton(
        SendTelegramMessage,
        bot=bot,
        chat_repo=chat_repo,
    )
