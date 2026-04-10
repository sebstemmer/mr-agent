import logging

from dependency_injector import containers, providers
from job_search.src.container import JobSearchContainer
from utils.src.config import settings
from utils.src.llm import CHAT_GPT_5_4_MINI_MODEL

from agent.job_search.src.get_jobs_tool import GetJobsTool
from agent.job_search.src.handle_job_search_node import HandleJobSearchNode
from agent.job_search.src.handle_job_search_tool import HandleJobSearchTool
from agent.job_search.src.job_search_status_tool import JobSearchStatusTool


class JobSearchAgentContainer(containers.DeclarativeContainer):
    job_search_container: JobSearchContainer = providers.DependenciesContainer()

    system_prompt = providers.Dependency(instance_of=str)

    get_jobs_tool = providers.Singleton(
        GetJobsTool,
        job_repo=job_search_container.job_repo,
        refresh_jobs=job_search_container.refresh_jobs,
    )
    job_search_status_tool = providers.Singleton(
        JobSearchStatusTool,
        state_repo=job_search_container.state_repo,
    )
    handle_job_search_tool = providers.Singleton(HandleJobSearchTool)
    handle_job_search_node = providers.Singleton(
        HandleJobSearchNode,
        api_key=settings.OPENAI_API_KEY,
        model=CHAT_GPT_5_4_MINI_MODEL,
        system_prompt=system_prompt,
        get_jobs_tool=get_jobs_tool,
        job_search_status_tool=job_search_status_tool,
        logger=providers.Singleton(logging.getLogger, "job_search"),
    )
