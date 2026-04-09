from dependency_injector import containers, providers
from utils.src.config import settings

from conversation.src.handle_conversation import HandleConversation
from conversation.src.handle_conversation_tool import HandleConversationTool


class ConversationContainer(containers.DeclarativeContainer):
    handle_conversation = providers.Singleton(
        HandleConversation,
        api_key=settings.OPENAI_API_KEY,
        model="gpt-5.4-mini",
    )

    handle_conversation_tool = providers.Singleton(HandleConversationTool)
