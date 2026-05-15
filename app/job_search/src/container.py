from dependency_injector import containers, providers
from utils.utils.src.container import UtilsContainer

from job_search.src.get_interesting_jobs import GetInterestingJobs
from job_search.src.get_job_search_state import GetOrCreateJobSearchState
from job_search.src.job_opening_repository import JobOpeningRepository
from job_search.src.job_repository import JobRepository
from job_search.src.job_search_state_repository import JobSearchStateRepository
from job_search.src.like_job import LikeJob
from job_search.src.refresh_jobs import RefreshJobs


class JobSearchContainer(containers.DeclarativeContainer):
    utils_container: UtilsContainer = providers.DependenciesContainer()

    job_opening_repo = providers.Singleton(
        JobOpeningRepository, session_factory=utils_container.session_factory
    )
    job_repo = providers.Singleton(
        JobRepository, session_factory=utils_container.session_factory
    )
    state_repo = providers.Singleton(
        JobSearchStateRepository, session_factory=utils_container.session_factory
    )
    get_or_create_job_search_state = providers.Singleton(
        GetOrCreateJobSearchState,
        state_repo=state_repo,
    )
    refresh_jobs = providers.Singleton(
        RefreshJobs,
        client=utils_container.http_client,
        job_repo=job_repo,
        state_repo=state_repo,
        get_or_create_job_search_state=get_or_create_job_search_state,
    )
    get_interesting_jobs = providers.Singleton(
        GetInterestingJobs,
        job_repo=job_repo,
    )
    like_job = providers.Singleton(
        LikeJob,
        job_repo=job_repo,
    )
