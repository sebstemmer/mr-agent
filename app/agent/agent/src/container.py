import logging

from dependency_injector import containers, providers
from job_search.src.container import JobSearchContainer
from microsoft_todo.src.container import MicrosoftTodoContainer
from utils.common.src.config import settings
from utils.common.src.llm import CHAT_GPT_5_4_MINI_MODEL
from weather.src.container import WeatherContainer

from agent.agent.src.classify_intent_node import ClassifyIntentNode
from agent.agent.src.create_agent import CreateAgent
from agent.job_search.src.container import JobSearchAgentContainer
from agent.tasks.container import TasksSubgraphContainer
from agent.weather.src.container import WeatherAgentContainer

SYSTEM_PROMPT = (
    "You are a personal assistant. Today is {today}. "
    "Keep responses concise and do not repeat the same information."
)


class AgentContainer(containers.DeclarativeContainer):
    weather_container: WeatherContainer = providers.DependenciesContainer()
    job_search_container: JobSearchContainer = providers.DependenciesContainer()
    microsoft_todo_container: MicrosoftTodoContainer = providers.DependenciesContainer()

    weather_agent_container = providers.Container(
        WeatherAgentContainer,
        weather_container=weather_container,
        system_prompt=SYSTEM_PROMPT,
    )

    job_search_agent_container = providers.Container(
        JobSearchAgentContainer,
        job_search_container=job_search_container,
        system_prompt=SYSTEM_PROMPT,
    )

    tasks_subgraph_container = providers.Container(
        TasksSubgraphContainer,
        microsoft_todo_container=microsoft_todo_container,
        system_prompt=SYSTEM_PROMPT,
    )

    classify_intent_node = providers.Singleton(
        ClassifyIntentNode,
        api_key=settings.OPENAI_API_KEY,
        model=CHAT_GPT_5_4_MINI_MODEL,
        system_prompt=SYSTEM_PROMPT,
        handle_weather_tool=weather_agent_container.handle_weather_tool,
        handle_job_search_tool=job_search_agent_container.handle_job_search_tool,
        handle_tasks_tool=tasks_subgraph_container.handle_tasks_tool,
        logger=providers.Singleton(logging.getLogger, "agent"),
    )

    _create_agent = providers.Singleton(
        CreateAgent,
        classify_intent_node=classify_intent_node,
        handle_weather_node=weather_agent_container.handle_weather_node,
        handle_job_search_node=job_search_agent_container.handle_job_search_node,
        create_tasks_subgraph=tasks_subgraph_container.create_tasks_subgraph,
    )

    agent = providers.Singleton(
        lambda create_agent: create_agent.create(),
        create_agent=_create_agent,
    )
