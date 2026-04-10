import httpx
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

_FORMAT_PROMPT = (
    "Format the following weather data into a readable summary in English. "
    "2 sentences max.\n\n{raw_weather}"
)


class GetWeather:
    def __init__(self, http_client: httpx.AsyncClient, api_key: str, model: str):
        self._http_client = http_client
        # noinspection PyTypeChecker
        self._llm = ChatOpenAI(api_key=api_key, model=model)

    async def get(self, location: str, day: int) -> str:
        if day < 0:
            return "Cannot look up weather in the past."
        if day > 2:
            return "Cannot forecast weather more than 2 days ahead."

        response = await self._http_client.get(
            f"https://wttr.in/{location}?3&T",
            headers={"User-Agent": "curl", "Accept-Language": "en"},
        )
        text = response.text.strip()
        sections = text.split("┌─────────────┐")
        if len(sections) >= 2:
            # noinspection PyTypeChecker
            header = sections[0].split("\n")[0]
            # noinspection PyTypeChecker
            day_section = sections[day + 1] if day + 1 < len(sections) else sections[-1]
            text = header + "\n┌─────────────┐" + day_section

        print(text)
        formatted = await self._llm.ainvoke(
            [HumanMessage(content=_FORMAT_PROMPT.format(raw_weather=text))]
        )
        print(formatted)
        return formatted.content
