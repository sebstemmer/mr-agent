from pathlib import Path

import aiofiles

from files.src.file_repository import FileRepository
from files.src.unsupported_file_type_error import UnsupportedFileTypeError


class ParseHtmlFileToString:
    _SUPPORTED_EXTENSIONS = {".html", ".htm"}

    def __init__(self, file_repository: FileRepository, base_dir: str):
        self._file_repository = file_repository
        self._base_dir = Path(base_dir)

    async def parse(self, uuid: str) -> str:
        file = await self._file_repository.find_by_uuid(uuid=uuid)
        if file is None:
            raise ValueError(f"File not found: {uuid}")

        extension = Path(file.filename).suffix.lower()
        if extension not in self._SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                f"Unsupported file type: {file.filename}. Please upload an HTML file."
            )

        file_path = self._base_dir / file.uuid / file.filename
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            return await f.read()
