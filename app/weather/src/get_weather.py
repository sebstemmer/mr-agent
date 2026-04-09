import httpx
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

_FORMAT_PROMPT = (
    "Format the following weather data into a readable summary. "
    "2 sentences max.\n\n{raw_weather}"
)


class GetWeather:
    def __init__(self, http_client: httpx.AsyncClient, api_key: str, model: str):
        self._http_client = http_client
        # noinspection PyTypeChecker
        self._llm = ChatOpenAI(api_key=api_key, model=model)

    async def get(self, location: str, day: int) -> str:
        response = await self._http_client.get(
            f"https://wttr.in/{location}?3&T",
            headers={"User-Agent": "curl"},
        )
        text = response.text.strip()
        sections = text.split("┌─────────────┐")
        if len(sections) >= 2:
            header = sections[0].split("\n")[0]
            day_section = sections[day + 1] if day + 1 < len(sections) else sections[-1]
            text = header + "\n┌─────────────┐" + day_section

        formatted = await self._llm.ainvoke(
            [HumanMessage(content=_FORMAT_PROMPT.format(raw_weather=text))]
        )
        return formatted.content
