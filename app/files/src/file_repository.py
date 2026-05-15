from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import delete, select

from files.src.file_model import File


class FileRepository:
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def save(self, file: File) -> File:
        async with self._session_factory() as session:
            session.add(file)
            await session.commit()
            await session.refresh(file)
            return file

    async def find_by_uuid(self, uuid: str) -> File | None:
        async with self._session_factory() as session:
            result = await session.exec(select(File).where(File.uuid == uuid))
            return result.first()

    async def delete_by_uuid(self, uuid: str) -> None:
        async with self._session_factory() as session:
            await session.exec(delete(File).where(File.uuid == uuid))
            await session.commit()
