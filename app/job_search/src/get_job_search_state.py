from job_search.src.job_search_state_repository import JobSearchStateRepository
from job_search.src.search_state_model import SearchState


class GetOrCreateJobSearchState:
    def __init__(self, state_repo: JobSearchStateRepository):
        self._state_repo = state_repo

    async def get_or_create(self) -> SearchState:
        state = await self._state_repo.find()
        if not state:
            state = await self._state_repo.save(state=SearchState())
        return state
