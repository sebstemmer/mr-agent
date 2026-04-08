from datetime import date

from channels.telegram.src.send_telegram_message import SendTelegramMessage
from job_search.src.job_model import Job
from job_search.src.job_repository import JobRepository
from job_search.src.refresh_jobs import RefreshJobs


def _format_message(jobs: list[Job]) -> str:
    if not jobs:
        return "No interesting jobs today."

    lines = ["Good morning! Here are today's interesting jobs:\n"]
    for job in jobs:
        line = f"- {job.summary}"
        if job.link:
            line += f"\n  {job.link}"
        lines.append(line)

    return "\n\n".join(lines)


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

        message = _format_message(jobs=jobs)
        await self._send_telegram_message.send(message=message)
