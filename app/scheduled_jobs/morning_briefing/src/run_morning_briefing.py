from datetime import date

from channels.telegram.src.send_telegram_message import SendTelegramMessage
from job_search.src.format_jobs import format_jobs
from job_search.src.job_repository import JobRepository
from job_search.src.refresh_jobs import RefreshJobs


class RunMorningBriefing:
    def __init__(
        self,
        refresh_jobs: RefreshJobs,
        job_repo: JobRepository,
        send_telegram_message: SendTelegramMessage,
    ):
        self._refresh_jobs = refresh_jobs
        self._job_repo = job_repo
        self._send_telegram_message = send_telegram_message

    async def run(self) -> None:
        await self._refresh_jobs.refresh()

        jobs = await self._job_repo.find_by_of_interest_and_created_at(
            of_interest=True,
            created_at=date.today(),
        )

        message = format_jobs(jobs=jobs)
        await self._send_telegram_message.send(message=message)
