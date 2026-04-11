import logging

from sqlalchemy.ext.asyncio import async_sessionmaker

from utils.common.src.datetime_utils import utc_now
from utils.patcher.src.patch import Patch
from utils.patcher.src.version_model import Version
from utils.patcher.src.version_repository import VersionRepository


class Patcher:
    def __init__(
        self,
        session_factory: async_sessionmaker,
        version_repo: VersionRepository,
        patches: list[Patch],
        logger: logging.Logger,
    ):
        self._session_factory = session_factory
        self._version_repo = version_repo
        self._patches = sorted(patches, key=lambda p: p.version)
        self._logger = logger

    async def patch(self) -> None:
        version = await self._version_repo.find()
        current_version = version.version if version is not None else -1
        self._logger.info(f"current db version: {current_version}")

        pending = [patch for patch in self._patches if patch.version > current_version]

        if not pending:
            self._logger.info("no pending patches")
            return

        for patch in pending:
            self._logger.info(f"applying patch {patch.version}")
            async with self._session_factory() as session:
                await patch.apply(session=session)
            if version is None:
                version = Version(version=patch.version, applied_at=utc_now())
            else:
                version.version = patch.version
                version.applied_at = utc_now()
            version = await self._version_repo.save(version=version)
            self._logger.info(f"applied patch {patch.version}")
