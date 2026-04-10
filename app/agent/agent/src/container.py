import logging

from dependency_injector import containers, providers
from job_search.src.container import JobSearchContainer
from utils.src.config import settings
from weather.src.container import WeatherContainer

from agent.agent.src.agent import create_agent
from agent.agent.src.classify_intent_node import ClassifyIntentNode
from agent.job_search.src.container import JobSearchAgentContainer
from agent.weather.src.container import WeatherAgentContainer

SYSTEM_PROMPT = (
    "You are a personal assistant. Today is {today}. "
    "Keep responses concise and do not repeat the same information."
)


class AgentContainer(containers.DeclarativeContainer):
    weather_container: WeatherContainer = providers.DependenciesContainer()
    job_search_container: JobSearchContainer = providers.DependenciesContainer()

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

    classify_intent_node = providers.Singleton(
        ClassifyIntentNode,
        api_key=settings.OPENAI_API_KEY,
        model="gpt-5.4-mini",
        system_prompt=SYSTEM_PROMPT,
        handle_weather_tool=weather_agent_container.handle_weather_tool,
        handle_job_search_tool=job_search_agent_container.handle_job_search_tool,
        logger=providers.Singleton(logging.getLogger, "agent"),
    )

    agent = providers.Singleton(
        create_agent,
        classify_intent_node=classify_intent_node,
        handle_weather_node=weather_agent_container.handle_weather_node,
        handle_job_search_node=job_search_agent_container.handle_job_search_node,
    )
