import logging
from contextlib import asynccontextmanager
from zoneinfo import ZoneInfo

from agent_v2.agent.src.handle_incoming_message import HandleIncomingMessage
from channels.telegram.src.bot import TelegramBot
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import MessageHandler, filters

load_dotenv()

from apscheduler.triggers.cron import CronTrigger
from container import Container
from fastapi import FastAPI
from sqlmodel import SQLModel
from utils.common.src.config import settings

logging.basicConfig(level=settings.LOG_LEVEL, force=True)
# logging.getLogger("agent").setLevel(settings.LOG_LEVEL)
# logging.getLogger("weather").setLevel(settings.LOG_LEVEL)

container: Container = Container()


@asynccontextmanager
async def lifespan(_app):
    async with container.utils_container().engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    await container.utils_container().patcher_container().patcher().patch()

    scheduler = container.utils_container().scheduler()

    morning_briefing = container.morning_briefing().run_morning_briefing()
    scheduler.add_job(
        morning_briefing.run,
        trigger=CronTrigger(hour=7, minute=0, timezone=ZoneInfo("Europe/Berlin")),
    )

    scheduler.start()

    handle_incoming_message: HandleIncomingMessage = (
        container.agent_container.handle_incoming_message()  # noqa
    )

    async def on_telegram_message(update: Update, _context):
        await handle_incoming_message.handle(
            chat_id=str(update.effective_chat.id), text=update.message.text
        )

    telegram_bot: TelegramBot = (
        container.channels_container.telegram_channel_container.bot()  # noqa
    )
    telegram_bot.app.add_handler(MessageHandler(filters.TEXT, on_telegram_message))
    await telegram_bot.start()

    yield

    scheduler.shutdown()
    await telegram_bot.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(container.utils_container().health_controller().router)
