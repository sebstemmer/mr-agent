from dependency_injector import containers, providers
from utils.src.config import settings
from utils.src.container import UtilsContainer

from weather.src.get_weather import GetWeather


class WeatherContainer(containers.DeclarativeContainer):
    utils_container: UtilsContainer = providers.DependenciesContainer()

    get_weather = providers.Singleton(
        GetWeather,
        http_client=utils_container.http_client,
        api_key=settings.OPENAI_API_KEY,
        model="gpt-5.4-mini",
    )
