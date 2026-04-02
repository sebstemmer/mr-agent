from langchain_core.tools import tool
import httpx

from config import settings


@tool
async def search_jobs(query: str, location: str = "", page: int = 1) -> str:
    """Search for job listings. query is the job title or keywords (e.g. 'AI engineer'). location is optional (e.g. 'Berlin'). Returns up to 10 results per page."""
    search_query = f"{query} in {location}" if location else query
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://jsearch.p.rapidapi.com/search",
            params={
                "query": search_query,
                "page": page,
                "num_pages": 1,
                "country": "de",
                "date_posted": "all",
            },
            headers={
                "Content-Type": "application/json",
                "x-rapidapi-host": "jsearch.p.rapidapi.com",
                "x-rapidapi-key": settings.RAPIDAPI_KEY,
            },
        )
        data = response.json()
        jobs = data.get("data", [])
        if not jobs:
            return "No jobs found."
        results = []
        for job in jobs:
            results.append(
                f"- {job.get('job_title')} at {job.get('employer_name')}\n"
                f"  Location: {job.get('job_city', 'N/A')}, {job.get('job_country', 'N/A')}\n"
                f"  Link: {job.get('job_apply_link', 'N/A')}"
            )
        return "\n\n".join(results)
