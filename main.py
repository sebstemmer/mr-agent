from contextlib import asynccontextmanager

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from fastapi import FastAPI

from config import settings

telegram_app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()


@asynccontextmanager
async def lifespan(_app):
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()  # type: ignore

    yield

    await telegram_app.updater.stop()  # type: ignore
    await telegram_app.stop()
    await telegram_app.shutdown()


app = FastAPI(lifespan=lifespan)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def log_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update.message.text)
    await update.message.reply_text(f"you wrote me {update.message.text}")


telegram_app.add_handler(CommandHandler("hello", hello))
telegram_app.add_handler(MessageHandler(filters.TEXT, log_input))
