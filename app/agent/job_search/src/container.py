import logging

from dependency_injector import containers, providers
from files.src.container import FilesContainer
from job_search.src.container import JobSearchContainer
from agent.job_search.src.apply_job_opening_node import ApplyJobOpeningNode
from agent.job_search.src.apply_job_opening_tool import ApplyJobOpeningTool
from agent.job_search.src.create_job_opening_node import CreateJobOpeningNode
from agent.job_search.src.create_job_opening_tool import CreateJobOpeningTool
from agent.job_search.src.delete_job_opening_node import DeleteJobOpeningNode
from agent.job_search.src.delete_job_opening_tool import DeleteJobOpeningTool
from agent.job_search.src.get_job_opening_details_node import GetJobOpeningDetailsNode
from agent.job_search.src.get_job_opening_details_tool import GetJobOpeningDetailsTool
from agent.job_search.src.get_job_openings_node import GetJobOpeningsNode
from agent.job_search.src.get_job_openings_tool import GetJobOpeningsTool
from agent.job_search.src.parse_job_opening import ParseJobOpening
from agent.job_search.src.get_jobs_node import GetJobsNode
from agent.job_search.src.get_jobs_tool import GetJobsTool
from agent.job_search.src.job_search_status_node import JobSearchStatusNode
from agent.job_search.src.job_search_status_tool import JobSearchStatusTool
from agent.job_search.src.like_job_node import LikeJobNode
from agent.job_search.src.like_job_tool import LikeJobTool


class JobSearchAgentContainer(containers.DeclarativeContainer):
    job_search_container: JobSearchContainer = providers.DependenciesContainer()
    files_container: FilesContainer = providers.DependenciesContainer()
    dispatch_executed_tool_action = providers.Dependency()

    _logger = providers.Singleton(logging.getLogger, "agent.job_search")

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

    _parse_job_opening = providers.Singleton(ParseJobOpening)

    create_job_opening_tool = providers.Singleton(
        CreateJobOpeningTool,
        job_opening_repo=job_search_container.job_opening_repo,
        parse_html_file_to_string=files_container.parse_html_file_to_string,
        parse_job_opening=_parse_job_opening,
        delete_file=files_container.delete_file,
    )

    create_job_opening_node = providers.Singleton(
        CreateJobOpeningNode,
        create_job_opening_tool=create_job_opening_tool,
        dispatch_executed_tool_action=dispatch_executed_tool_action,
        delete_file=files_container.delete_file,
        logger=_logger,
    )

    get_job_openings_tool = providers.Singleton(
        GetJobOpeningsTool,
        job_opening_repo=job_search_container.job_opening_repo,
    )

    get_job_openings_node = providers.Singleton(
        GetJobOpeningsNode,
        get_job_openings_tool=get_job_openings_tool,
        dispatch_executed_tool_action=dispatch_executed_tool_action,
        logger=_logger,
    )

    get_job_opening_details_tool = providers.Singleton(
        GetJobOpeningDetailsTool,
        job_opening_repo=job_search_container.job_opening_repo,
    )

    get_job_opening_details_node = providers.Singleton(
        GetJobOpeningDetailsNode,
        get_job_opening_details_tool=get_job_opening_details_tool,
        dispatch_executed_tool_action=dispatch_executed_tool_action,
        logger=_logger,
    )

    delete_job_opening_tool = providers.Singleton(
        DeleteJobOpeningTool,
        job_opening_repo=job_search_container.job_opening_repo,
    )

    delete_job_opening_node = providers.Singleton(
        DeleteJobOpeningNode,
        delete_job_opening_tool=delete_job_opening_tool,
        dispatch_executed_tool_action=dispatch_executed_tool_action,
        logger=_logger,
    )

    apply_job_opening_tool = providers.Singleton(
        ApplyJobOpeningTool,
        apply_job_opening=job_search_container.apply_job_opening,
    )

    apply_job_opening_node = providers.Singleton(
        ApplyJobOpeningNode,
        apply_job_opening_tool=apply_job_opening_tool,
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
