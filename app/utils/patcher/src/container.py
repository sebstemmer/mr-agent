import logging

from dependency_injector import containers, providers
from patches.src.registry import PATCHES
from sqlalchemy.ext.asyncio.session import AsyncSession

from utils.patcher.src.patcher import Patcher
from utils.patcher.src.version_repository import VersionRepository


class PatcherContainer(containers.DeclarativeContainer):
    session = providers.Dependency(instance_of=AsyncSession)

    version_repo = providers.Singleton(VersionRepository, session=session)
    patcher = providers.Singleton(
        Patcher,
        session=session,
        version_repo=version_repo,
        patches=providers.Object(PATCHES),
        logger=providers.Singleton(logging.getLogger, "patcher"),
    )
