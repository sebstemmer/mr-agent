import logging

from dependency_injector import containers, providers
from utils.common.src.config import settings
from utils.utils.src.container import UtilsContainer

from microsoft_todo.src.microsoft_todo_client import MicrosoftTodoClient


class MicrosoftTodoContainer(containers.DeclarativeContainer):
    utils_container: UtilsContainer = providers.DependenciesContainer()

    microsoft_todo_client = providers.Singleton(
        MicrosoftTodoClient,
        client=utils_container.http_client,
        client_id=settings.MICROSOFT_CLIENT_ID,
        client_secret=settings.MICROSOFT_CLIENT_SECRET,
        refresh_token=settings.MICROSOFT_REFRESH_TOKEN,
        logger=providers.Singleton(logging.getLogger, "microsoft_todo"),
    )
