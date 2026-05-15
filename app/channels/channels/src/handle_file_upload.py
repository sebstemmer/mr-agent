from dataclasses import dataclass

from files.src.file_model import File
from files.src.save_file import SaveFile


@dataclass
class FileUploadResult:
    file: File
    message: str | None


class HandleFileUpload:
    def __init__(self, save_file: SaveFile):
        self._save_file = save_file

    async def handle(
        self, filename: str, filetype: str, content: bytes, message: str | None
    ) -> FileUploadResult:
        saved_file = await self._save_file.save(
            filename=filename, filetype=filetype, content=content
        )

        return FileUploadResult(file=saved_file, message=message)
