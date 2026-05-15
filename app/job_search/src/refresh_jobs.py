import json
import logging
import secrets
import string
from datetime import date

import httpx
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from utils.common.src.config import settings
from utils.common.src.llm import CHAT_GPT_5_4_MODEL

from job_search.src.get_job_search_state import GetOrCreateJobSearchState
from job_search.src.job_model import Job
from job_search.src.job_repository import JobRepository
from job_search.src.job_search_state_repository import JobSearchStateRepository

_evaluation_llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model=CHAT_GPT_5_4_MODEL)
_evaluation_llm_json = _evaluation_llm.bind(response_format={"type": "json_object"})

_EVALUATION_PROMPT = f"""You are a job posting evaluator. Determine if a job posting is interesting for the user, explain why, and provide a summary.

User profile:
{settings.JOB_CLASSIFICATION_PROMPT}

Respond with JSON only: {{"reason": "<one sentence why this job is or is not interesting for the user>", "decision": "yes" or "no", "summary": "<2-3 sentence summary of the job posting>"}}"""

logger = logging.getLogger(__name__)

_REQUIRED_JOB_FIELDS = ["job_title", "employer_name", "job_description"]


async def _evaluate(
    job_title: str, employer_name: str, job_description: str
) -> tuple[bool, str]:
    response = await _evaluation_llm_json.ainvoke(
        [
            SystemMessage(content=_EVALUATION_PROMPT),
            HumanMessage(
                content=f"Job title: {job_title}\nEmployer: {employer_name}\n\nJob description:\n{job_description}"
            ),
        ]
    )
    data = json.loads(response.content)
    return data["decision"] == "yes", data["summary"]


class RefreshJobs:
    def __init__(
        self,
        client: httpx.AsyncClient,
        job_repo: JobRepository,
        state_repo: JobSearchStateRepository,
        get_or_create_job_search_state: GetOrCreateJobSearchState,
    ):
        self._client = client
        self._job_repo = job_repo
        self._state_repo = state_repo
        self._get_job_search_state = get_or_create_job_search_state

    async def refresh(self) -> None:
        state = await self._get_job_search_state.get_or_create()

        if state.last_searched_at == date.today():
            return

        if not state.last_searched_at:
            date_posted = "all"
            num_pages = settings.INIT_JOB_SEARCH_MAX_PAGES
        else:
            date_posted = "today"
            num_pages = settings.JOB_SEARCH_MAX_PAGES

        jobs = await self._fetch_jobs(date_posted=date_posted, num_pages=num_pages)

        for job in jobs:
            await self._process_job(job=job)

        await self._state_repo.set_last_searched_at(value=date.today())

    async def _process_job(self, job: dict) -> None:
        job_id = job.get("job_id")
        if not job_id:
            logger.error("Job is missing 'job_id', skipping: %s", job)
            return

        if await self._job_repo.exists_by_id(job_id=job_id):
            return

        for field in _REQUIRED_JOB_FIELDS:
            if field not in job:
                logger.warning("Job %s is missing field '%s'", job_id, field)

        interesting, summary = await _evaluate(
            job_title=job.get("job_title", ""),
            employer_name=job.get("employer_name", ""),
            job_description=job.get("job_description", ""),
        )

        link = await self._resolve_link(job=job)

        db_job = Job(
            public_id=self._generate_public_id(),
            job_id=job_id,
            of_interest=interesting,
            link=link,
            summary=summary,
        )
        await self._job_repo.save(job=db_job)

    async def _fetch_jobs(self, date_posted: str, num_pages: int) -> list[dict]:
        all_jobs = []
        # noinspection PyTypeChecker
        for page in range(1, num_pages + 1):
            response = await self._client.get(
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
                return all_jobs
            all_jobs.extend(jobs)
        return all_jobs

    async def _check_link(self, url: str) -> bool:
        if not url:
            return False
        try:
            response = await self._client.head(url)
            return response.status_code < 400
        except httpx.HTTPError:
            return False

    @staticmethod
    def _generate_public_id() -> str:
        alphabet = string.ascii_lowercase + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(5))

    async def _resolve_link(self, job: dict) -> str | None:
        apply_link = job.get("job_apply_link")
        if apply_link and await self._check_link(url=apply_link):
            return apply_link

        google_link = job.get("job_google_link")
        if google_link and await self._check_link(url=google_link):
            return google_link

        return None
