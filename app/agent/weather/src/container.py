import logging

from dependency_injector import containers, providers
from utils.src.config import settings
from utils.src.container import UtilsContainer
from weather.src.container import WeatherContainer

from agent.weather.src.get_weather_tool import GetWeatherTool
from agent.weather.src.handle_weather_node import HandleWeatherNode
from agent.weather.src.handle_weather_tool import HandleWeatherTool


class WeatherAgentContainer(containers.DeclarativeContainer):
    system_prompt = providers.Dependency(instance_of=str)

    utils_container: UtilsContainer = providers.DependenciesContainer()
    weather_container: WeatherContainer = providers.DependenciesContainer()

    get_weather_tool = providers.Singleton(
        GetWeatherTool, get_weather=weather_container.get_weather
    )
    handle_weather_tool = providers.Singleton(HandleWeatherTool)

    handle_weather_node = providers.Singleton(
        HandleWeatherNode,
        api_key=settings.OPENAI_API_KEY,
        model="gpt-5.4-mini",
        system_prompt=system_prompt,
        get_weather_tool=get_weather_tool,
        logger=providers.Singleton(logging.getLogger, "weather"),
    )
