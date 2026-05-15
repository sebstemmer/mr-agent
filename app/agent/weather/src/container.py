import logging

from dependency_injector import containers, providers
from weather.src.container import WeatherContainer

from agent.weather.src.get_weather_node import GetWeatherNode
from agent.weather.src.get_weather_tool import GetWeatherTool


class WeatherAgentContainer(containers.DeclarativeContainer):
    weather_container: WeatherContainer = providers.DependenciesContainer()
    dispatch_executed_tool_action = providers.Dependency()

    get_weather_tool = providers.Singleton(
        GetWeatherTool, get_weather=weather_container.get_weather
    )

    get_weather_node = providers.Singleton(
        GetWeatherNode,
        get_weather_tool=get_weather_tool,
        dispatch_executed_tool_action=dispatch_executed_tool_action,
        logger=providers.Singleton(logging.getLogger, "agent.weather"),
    )
