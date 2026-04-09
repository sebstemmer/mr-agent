import logging

from conversation.src.handle_conversation import HandleConversation
from conversation.src.handle_conversation_tool import HandleConversationTool
from dependency_injector import containers, providers
from job_search.src.handle_job_search import HandleJobSearch
from job_search.src.handle_job_search_tool import HandleJobSearchTool
from utils.src.config import settings
from weather.src.handle_weather import HandleWeather
from weather.src.handle_weather_tool import HandleWeatherTool

from agent.src.agent import create_agent
from agent.src.classify_intent import ClassifyIntent


class AgentContainer(containers.DeclarativeContainer):
    handle_conversation = providers.Dependency(instance_of=HandleConversation)
    handle_conversation_tool = providers.Dependency(instance_of=HandleConversationTool)
    handle_weather = providers.Dependency(instance_of=HandleWeather)
    handle_weather_tool = providers.Dependency(instance_of=HandleWeatherTool)
    handle_job_search = providers.Dependency(instance_of=HandleJobSearch)
    handle_job_search_tool = providers.Dependency(instance_of=HandleJobSearchTool)

    classify_intent = providers.Singleton(
        ClassifyIntent,
        api_key=settings.OPENAI_API_KEY,
        model="gpt-5.4-mini",
        handle_conversation=handle_conversation,
        handle_conversation_tool=handle_conversation_tool,
        handle_weather=handle_weather,
        handle_weather_tool=handle_weather_tool,
        handle_job_search=handle_job_search,
        handle_job_search_tool=handle_job_search_tool,
        logger=providers.Singleton(logging.getLogger, "agent"),
    )

    agent = providers.Singleton(
        create_agent,
        classify_intent=classify_intent,
        handle_weather=handle_weather,
        handle_job_search=handle_job_search,
    )
