import logging

from dependency_injector import containers, providers
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.src.config import settings

from job_search.src.get_job_search_state import GetOrCreateJobSearchState
from job_search.src.get_jobs_tool import GetJobsTool
from job_search.src.handle_job_search import HandleJobSearch
from job_search.src.handle_job_search_tool import HandleJobSearchTool
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
    handle_job_search_tool = providers.Singleton(HandleJobSearchTool)
    handle_job_search = providers.Singleton(
        HandleJobSearch,
        api_key=settings.OPENAI_API_KEY,
        model="gpt-5.4-mini",
        get_jobs_tool=get_jobs_tool,
        job_search_status_tool=job_search_status_tool,
        logger=providers.Singleton(logging.getLogger, "job_search"),
    )
