from datetime import date

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import select, update

from job_search.src.search_state_model import SearchState


class JobSearchStateRepository:
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def find(self) -> SearchState | None:
        async with self._session_factory() as session:
            result = await session.exec(select(SearchState))
            return result.first()

    async def save(self, state: SearchState) -> SearchState:
        async with self._session_factory() as session:
            session.add(state)
            await session.commit()
            await session.refresh(state)
            return state

    async def set_last_searched_at(self, value: date) -> None:
        async with self._session_factory() as session:
            await session.exec(update(SearchState).values(last_searched_at=value))
            await session.commit()
