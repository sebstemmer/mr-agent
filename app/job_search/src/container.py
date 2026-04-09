from dependency_injector import containers, providers
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from job_search.src.get_job_search_state import GetOrCreateJobSearchState
from job_search.src.get_jobs_tool import GetJobsTool
from job_search.src.job_repository import JobRepository
from job_search.src.job_search_state_repository import JobSearchStateRepository
from job_search.src.job_search_status_tool import JobSearchStatusTool
from job_search.src.refresh_jobs import RefreshJobs


class JobSearchContainer(containers.DeclarativeContainer):
    session = providers.Dependency(instance_of=AsyncSession)
    http_client = providers.Dependency(instance_of=AsyncClient)

    job_repo = providers.Singleton(JobRepository, session=session)
    state_repo = providers.Singleton(JobSearchStateRepository, session=session)
    get_job_search_state = providers.Singleton(
        GetOrCreateJobSearchState,
        state_repo=state_repo,
    )
    refreshJobs = providers.Singleton(
        RefreshJobs,
        client=http_client,
        job_repo=job_repo,
        state_repo=state_repo,
        get_job_search_state=get_job_search_state,
    )
    get_jobs_tool = providers.Singleton(
        GetJobsTool,
        job_repo=job_repo,
        refresh_jobs=refreshJobs,
    )
    job_search_status_tool = providers.Singleton(
        JobSearchStatusTool,
        state_repo=state_repo,
    )
