import logging

from dependency_injector import containers, providers
from patches.src.registry import PATCHES
from sqlalchemy.ext.asyncio import async_sessionmaker

from utils.patcher.src.patcher import Patcher
from utils.patcher.src.version_repository import VersionRepository


class PatcherContainer(containers.DeclarativeContainer):
    session_factory = providers.Dependency(instance_of=async_sessionmaker)

    version_repo = providers.Singleton(
        VersionRepository, session_factory=session_factory
    )
    patcher = providers.Singleton(
        Patcher,
        session_factory=session_factory,
        version_repo=version_repo,
        patches=providers.Object(PATCHES),
        logger=providers.Singleton(logging.getLogger, "patcher"),
    )
