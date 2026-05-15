import shutil
from pathlib import Path

from files.src.file_repository import FileRepository


class DeleteFile:
    def __init__(self, file_repository: FileRepository, base_dir: str):
        self._file_repository = file_repository
        self._base_dir = Path(base_dir)

    async def delete(self, uuid: str) -> None:
        file_dir = self._base_dir / uuid
        if file_dir.exists():
            shutil.rmtree(file_dir)

        await self._file_repository.delete_by_uuid(uuid=uuid)
