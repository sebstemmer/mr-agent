import logging

from dependency_injector import containers, providers
from httpx import AsyncClient
from utils.src.config import settings

from weather.src.get_weather import GetWeather
from weather.src.get_weather_tool import GetWeatherTool
from weather.src.handle_weather import HandleWeather
from weather.src.handle_weather_tool import HandleWeatherTool


class WeatherContainer(containers.DeclarativeContainer):
    http_client = providers.Dependency(instance_of=AsyncClient)

    get_weather = providers.Singleton(
        GetWeather,
        http_client=http_client,
        api_key=settings.OPENAI_API_KEY,
        model="gpt-5.4-mini",
    )
    get_weather_tool = providers.Singleton(GetWeatherTool, get_weather=get_weather)
    handle_weather_tool = providers.Singleton(HandleWeatherTool)

    handle_weather = providers.Singleton(
        HandleWeather,
        api_key=settings.OPENAI_API_KEY,
        model="gpt-5.4-mini",
        get_weather_tool=get_weather_tool,
        logger=providers.Singleton(logging.getLogger, "weather"),
    )
