import logging

from dependency_injector import containers, providers
from utils.src.config import settings
from utils.src.llm import CHAT_GPT_5_4_MINI_MODEL
from weather.src.container import WeatherContainer

from agent.weather.src.get_weather_tool import GetWeatherTool
from agent.weather.src.handle_weather_node import HandleWeatherNode
from agent.weather.src.handle_weather_tool import HandleWeatherTool


class WeatherAgentContainer(containers.DeclarativeContainer):
    system_prompt = providers.Dependency(instance_of=str)

    weather_container: WeatherContainer = providers.DependenciesContainer()

    get_weather_tool = providers.Singleton(
        GetWeatherTool, get_weather=weather_container.get_weather
    )
    handle_weather_tool = providers.Singleton(HandleWeatherTool)

    handle_weather_node = providers.Singleton(
        HandleWeatherNode,
        api_key=settings.OPENAI_API_KEY,
        model=CHAT_GPT_5_4_MINI_MODEL,
        system_prompt=system_prompt,
        get_weather_tool=get_weather_tool,
        logger=providers.Singleton(logging.getLogger, "weather"),
    )
