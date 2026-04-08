import json
from datetime import date
from typing import Type

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
import httpx

from utils.src.config import settings
from job_search.src.search_state_model import Job
from job_search.src.job_repository import JobRepository
from job_search.src.job_search_state_repository import JobSearchStateRepository

_classification_llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-5.4-mini")

_CLASSIFICATION_PROMPT = f"""You are a job posting classifier. Determine if a job posting is interesting for the user.

User profile:
{settings.JOB_CLASSIFICATION_PROMPT}

Respond with JSON only: {{"reason": "<one sentence why>", "decision": "yes" or "no", "summary": "<2-3 sentence summary of the job posting>"}}"""

_classification_llm_json = _classification_llm.bind(response_format={"type": "json_object"})


async def _is_interesting(job_title: str, employer_name: str, job_description: str) -> tuple[bool, str]:
    response = await _classification_llm_json.ainvoke([
        SystemMessage(content=_CLASSIFICATION_PROMPT),
        HumanMessage(content=f"Job title: {job_title}\nEmployer: {employer_name}\n\nJob description:\n{job_description}"),
    ])
    data = json.loads(response.content)
    return data["decision"] == "yes", data["summary"]


async def _fetch_jobs(date_posted: str, num_pages: int) -> list[dict]:
    all_jobs = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for page in range(1, num_pages + 1):
            response = await client.get(
                "https://jsearch.p.rapidapi.com/search",
                params={
                    "query": settings.JOB_SEARCH_QUERY,
                    "page": page,
                    "num_pages": 1,
                    "country": "de",
                    "date_posted": date_posted,
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
                break
            all_jobs.extend(jobs)
    return all_jobs


async def _check_link(url: str) -> bool:
    if not url:
        return False
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.head(url)
            return response.status_code < 400
    except Exception:
        return False


async def _resolve_link(job: dict) -> tuple[str, bool]:
    apply_link = job.get("job_apply_link", "")
    if await _check_link(url=apply_link):
        return apply_link, False

    google_link = job.get("job_google_link", "")
    if await _check_link(url=google_link):
        return google_link, False

    return apply_link or google_link or "", True


class SearchJobsInput(BaseModel):
    pass


class JobsTool(BaseTool):
    name: str = "get_jobs"
    description: str = "Returns all interesting job postings. Automatically searches for new jobs if not searched today. Each result includes a summary and application link."
    args_schema: Type[BaseModel] = SearchJobsInput
    job_repo: JobRepository
    state_repo: JobSearchStateRepository

    class Config:
        arbitrary_types_allowed = True

    async def _search_new_jobs(self) -> None:
        state = self.state_repo.get()

        if not state.last_searched_at:
            date_posted = "all"
            num_pages = settings.INIT_JOB_SEARCH_MAX_PAGES
        else:
            date_posted = "today"
            num_pages = 1

        jobs = await _fetch_jobs(date_posted=date_posted, num_pages=num_pages)

        for job in jobs:
            job_id = job.get("job_id")
            if self.job_repo.exists(job_id=job_id):
                continue

            interesting, summary = await _is_interesting(
                job_title=job.get("job_title", ""),
                employer_name=job.get("employer_name", ""),
                job_description=job.get("job_description", ""),
            )

            link, is_dead = await _resolve_link(job=job)

            db_job = Job(
                job_id=job_id,
                of_interest=interesting,
                link=link,
                is_dead=is_dead,
                summary=summary,
            )
            self.job_repo.save(job=db_job)

        self.state_repo.update_last_searched_at(value=date.today())

    async def _arun(self) -> str:
        state = self.state_repo.get()

        if state.last_searched_at != date.today():
            await self._search_new_jobs()

        jobs = self.job_repo.find_all_interesting()
        if not jobs:
            return "No interesting jobs found."

        results = []
        for job in jobs:
            results.append(
                f"{job.summary}\n"
                f"{job.link}"
            )
        return "\n#########\n".join(results)

    def _run(self) -> str:
        raise NotImplementedError("Use _arun")
