import logging

from dependency_injector import containers, providers
from weather.src.container import WeatherContainer

from agent_v2.weather.src.get_weather_node import GetWeatherNode
from agent_v2.weather.src.get_weather_tool import GetWeatherTool


class WeatherAgentContainer(containers.DeclarativeContainer):
    weather_container: WeatherContainer = providers.DependenciesContainer()

    get_weather_tool = providers.Singleton(
        GetWeatherTool, get_weather=weather_container.get_weather
    )

    get_weather_node = providers.Singleton(
        GetWeatherNode,
        get_weather_tool=get_weather_tool,
        logger=providers.Singleton(logging.getLogger, "agent_v2.weather"),
    )
