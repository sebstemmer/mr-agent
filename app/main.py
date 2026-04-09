import logging
from contextlib import asynccontextmanager

from apscheduler.triggers.cron import CronTrigger
from container import Container
from fastapi import FastAPI
from sqlmodel import SQLModel
from utils.src.config import settings

logging.basicConfig(level=settings.LOG_LEVEL, force=True)
logging.getLogger("agent").setLevel(settings.LOG_LEVEL)
logging.getLogger("weather").setLevel(settings.LOG_LEVEL)

container = Container()


@asynccontextmanager
async def lifespan(_app):
    async with container.utils().engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    scheduler = container.utils().scheduler()

    morning_briefing = container.morning_briefing().run_morning_briefing()
    scheduler.add_job(
        morning_briefing.run,
        trigger=CronTrigger(hour=7, minute=0),
    )

    scheduler.start()

    telegram_bot = container.telegram().bot()
    await telegram_bot.start()

    yield

    scheduler.shutdown()
    await telegram_bot.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(container.utils().health_controller().router)
