import uuid as uuid_lib
from pathlib import Path

import aiofiles

from files.src.file_model import File
from files.src.file_repository import FileRepository


class SaveFile:
    def __init__(self, file_repository: FileRepository, base_dir: str):
        self._file_repository = file_repository
        self._base_dir = Path(base_dir)

    async def save(self, filename: str, filetype: str, content: bytes) -> File:
        file_uuid = str(uuid_lib.uuid4())
        file_dir = self._base_dir / file_uuid
        file_dir.mkdir(parents=True, exist_ok=True)

        file_path = file_dir / filename
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        return await self._file_repository.save(
            file=File(uuid=file_uuid, filename=filename, filetype=filetype),
        )
