from datetime import date

from agent.job_search.src.format_jobs import format_jobs
from channels.telegram.src.send_telegram_message import SendTelegramMessage
from job_search.src.get_interesting_jobs import GetInterestingJobs
from job_search.src.refresh_jobs import RefreshJobs


class RunMorningBriefing:
    def __init__(
        self,
        refresh_jobs: RefreshJobs,
        get_interesting_jobs: GetInterestingJobs,
        send_telegram_message: SendTelegramMessage,
    ):
        self._refresh_jobs = refresh_jobs
        self._get_interesting_jobs = get_interesting_jobs
        self._send_telegram_message = send_telegram_message

    async def run(self) -> None:
        await self._refresh_jobs.refresh()

        today = date.today()
        jobs = await self._get_interesting_jobs.get(
            start_date=today,
            end_date=today,
        )

        message = format_jobs(jobs=jobs)
        await self._send_telegram_message.send(message=message)
