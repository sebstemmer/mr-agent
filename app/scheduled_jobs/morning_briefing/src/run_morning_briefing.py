import asyncio

from agent.tasks.src.format_task import format_task
from channels.telegram.src.send_telegram_message import SendTelegramMessage
from job_search.src.get_interesting_jobs import GetInterestingJobs
from job_search.src.refresh_jobs import RefreshJobs
from microsoft_todo.src.microsoft_todo_client import MicrosoftTodoClient
from microsoft_todo.src.task_status import TaskStatus
from utils.common.src.datetime_utils import today_berlin
from weather.src.get_weather import GetWeather


class RunMorningBriefing:
    def __init__(
        self,
        greeting: str,
        weather_location: str,
        personal_todo_list_id: str,
        refresh_jobs: RefreshJobs,
        get_interesting_jobs: GetInterestingJobs,
        get_weather: GetWeather,
        todo_client: MicrosoftTodoClient,
        send_telegram_message: SendTelegramMessage,
    ):
        self._greeting = greeting
        self._weather_location = weather_location
        self._personal_todo_list_id = personal_todo_list_id
        self._refresh_jobs = refresh_jobs
        self._get_interesting_jobs = get_interesting_jobs
        self._get_weather = get_weather
        self._todo_client = todo_client
        self._send_telegram_message = send_telegram_message

    async def run(self) -> None:
        today = today_berlin()

        weather, tasks, jobs = await asyncio.gather(
            self._get_weather.get(location=self._weather_location, day=0),
            self._todo_client.find_by_status_and_due_date_between_inclusive(
                list_id=self._personal_todo_list_id,
                status=TaskStatus.NOT_STARTED,
                due_from=today,
                due_to=today,
            ),
            self._refresh_and_get_jobs(today=today),
        )

        _SEP = "\n\n#########\n\n"
        sections = [
            self._greeting,
            f"*Weather*\n\n{weather}",
            self._format_tasks_section(tasks=tasks),
            f"*Jobs*\n\n{len(jobs)} new interesting jobs found today.",
        ]

        message = _SEP.join(sections)
        await self._send_telegram_message.send(message=message)

    async def _refresh_and_get_jobs(self, today):
        await self._refresh_jobs.refresh()
        return await self._get_interesting_jobs.get(
            start_date=today,
            end_date=today,
        )

    @staticmethod
    def _format_tasks_section(tasks: list[dict]) -> str:
        if not tasks:
            return "*Today's Tasks*\n\nNo tasks due today."
        lines = [
            f"{index}. {format_task(task=task)}"
            for index, task in enumerate(tasks, start=1)
        ]
        return "*Today's Tasks*\n\n" + "\n".join(lines)
