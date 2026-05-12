import logging

from dependency_injector import containers, providers
from job_search.src.container import JobSearchContainer

from agent.job_search.src.get_jobs_node import GetJobsNode
from agent.job_search.src.get_jobs_tool import GetJobsTool
from agent.job_search.src.job_search_status_node import JobSearchStatusNode
from agent.job_search.src.job_search_status_tool import JobSearchStatusTool
from agent.job_search.src.like_job_node import LikeJobNode
from agent.job_search.src.like_job_tool import LikeJobTool


class JobSearchAgentContainer(containers.DeclarativeContainer):
    job_search_container: JobSearchContainer = providers.DependenciesContainer()
    dispatch_executed_tool_action = providers.Dependency()

    _logger = providers.Singleton(logging.getLogger, "agent_v2.job_search")

    get_jobs_tool = providers.Singleton(
        GetJobsTool,
        get_interesting_jobs=job_search_container.get_interesting_jobs,
        refresh_jobs=job_search_container.refresh_jobs,
    )

    get_jobs_node = providers.Singleton(
        GetJobsNode,
        get_jobs_tool=get_jobs_tool,
        dispatch_executed_tool_action=dispatch_executed_tool_action,
        logger=_logger,
    )

    like_job_tool = providers.Singleton(
        LikeJobTool,
        like_job=job_search_container.like_job,
    )

    like_job_node = providers.Singleton(
        LikeJobNode,
        like_job_tool=like_job_tool,
        dispatch_executed_tool_action=dispatch_executed_tool_action,
        logger=_logger,
    )

    job_search_status_tool = providers.Singleton(
        JobSearchStatusTool,
        state_repo=job_search_container.state_repo,
    )

    job_search_status_node = providers.Singleton(
        JobSearchStatusNode,
        job_search_status_tool=job_search_status_tool,
        dispatch_executed_tool_action=dispatch_executed_tool_action,
        logger=_logger,
    )
