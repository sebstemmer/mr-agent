from langchain_core.tools import tool
import httpx

@tool
async def get_weather(location: str, day: int = 0) -> str:
    """Get weather forecast for a given location. day=0 for today, day=1 for tomorrow, day=2 for the day after tomorrow. Only supports up to 2 days ahead (today + 2). Cannot provide weather beyond that range."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://wttr.in/{location}?3&T",
            headers={"User-Agent": "curl"},
        )
        text = response.text.strip()
        sections = text.split("┌─────────────┐")
        if len(sections) >= 2:
            header = sections[0].split("\n")[0]
            # sections[1] = today, sections[2] = tomorrow, sections[3] = day after
            day_section = sections[day + 1] if day + 1 < len(sections) else sections[-1]
            text = header + "\n┌─────────────┐" + day_section
        print("")
        print("response from agent")
        print(text)
        print("")
        return text