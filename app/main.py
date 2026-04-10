import logging
from contextlib import asynccontextmanager
from zoneinfo import ZoneInfo

from apscheduler.triggers.cron import CronTrigger
from container import Container
from fastapi import FastAPI
from sqlmodel import SQLModel
from utils.src.config import settings

logging.basicConfig(level=settings.LOG_LEVEL, force=True)
logging.getLogger("agent").setLevel(settings.LOG_LEVEL)
logging.getLogger("weather").setLevel(settings.LOG_LEVEL)

container: Container = Container()


@asynccontextmanager
async def lifespan(_app):
    async with container.utils_container().engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    scheduler = container.utils_container().scheduler()

    morning_briefing = container.morning_briefing().run_morning_briefing()
    scheduler.add_job(
        morning_briefing.run,
        trigger=CronTrigger(hour=7, minute=0, timezone=ZoneInfo("Europe/Berlin")),
    )

    scheduler.start()

    telegram_bot = container.channels_container.telegram_channel_container.bot()
    await telegram_bot.start()

    yield

    scheduler.shutdown()
    await telegram_bot.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(container.utils_container().health_controller().router)
