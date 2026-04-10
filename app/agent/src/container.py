import logging

from dependency_injector import containers, providers
from job_search.src.handle_job_search_node import HandleJobSearchNode
from job_search.src.handle_job_search_tool import HandleJobSearchTool
from utils.src.config import settings
from weather.src.handle_weather_node import HandleWeatherNode
from weather.src.handle_weather_tool import HandleWeatherTool

from agent.src.agent import create_agent
from agent.src.classify_intent_node import ClassifyIntentNode

SYSTEM_PROMPT = (
    "You are a personal assistant. Today is {today}. "
    "Keep responses concise and do not repeat the same information."
)


class AgentContainer(containers.DeclarativeContainer):
    handle_weather_node = providers.Dependency(instance_of=HandleWeatherNode)
    handle_weather_tool = providers.Dependency(instance_of=HandleWeatherTool)
    handle_job_search_node = providers.Dependency(instance_of=HandleJobSearchNode)
    handle_job_search_tool = providers.Dependency(instance_of=HandleJobSearchTool)

    classify_intent_node = providers.Singleton(
        ClassifyIntentNode,
        api_key=settings.OPENAI_API_KEY,
        model="gpt-5.4-mini",
        system_prompt=SYSTEM_PROMPT,
        handle_weather_tool=handle_weather_tool,
        handle_job_search_tool=handle_job_search_tool,
        logger=providers.Singleton(logging.getLogger, "agent"),
    )

    agent = providers.Singleton(
        create_agent,
        classify_intent_node=classify_intent_node,
        handle_weather_node=handle_weather_node,
        handle_job_search_node=handle_job_search_node,
    )
