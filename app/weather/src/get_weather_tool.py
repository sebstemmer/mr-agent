from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from utils.src.sync_run_not_implemented import SyncRunNotImplemented

from weather.src.get_weather import GetWeather


class GetWeatherInput(BaseModel):
    location: str = Field(description="City or location name")
    day: int = Field(
        description="0 for today, 1 for tomorrow, 2 for the day after tomorrow. Only supports up to 2 days ahead."
    )


class GetWeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "Returns the weather forecast for a given location and day."
    args_schema: Type[BaseModel] = GetWeatherInput
    get_weather: GetWeather

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, location: str, day: int) -> str:
        return await self.get_weather.get(location=location, day=day)

    def _run(self, location: str, day: int) -> str:
        raise SyncRunNotImplemented()
