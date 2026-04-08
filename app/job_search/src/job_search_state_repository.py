from datetime import date

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from job_search.src.search_state_model import SearchState


class JobSearchStateRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find(self) -> SearchState | None:
        result = await self._session.exec(select(SearchState))
        return result.first()

    async def save(self, state: SearchState) -> SearchState:
        self._session.add(state)
        await self._session.commit()
        await self._session.refresh(state)
        return state

    async def update_last_searched_at(self, state: SearchState, value: date) -> None:
        state.last_searched_at = value
        await self._session.commit()
