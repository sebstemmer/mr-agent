from channels.telegram.src.handle_telegram_init import HandleTelegramInit
from channels.telegram.src.handle_telegram_message import HandleTelegramMessage
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)


class TelegramBot:
    def __init__(
        self,
        token: str,
        handle_init: HandleTelegramInit,
        handle_message: HandleTelegramMessage,
    ):
        self._app = ApplicationBuilder().token(token).build()
        self._app.add_handler(CommandHandler("init", handle_init.handle))
        self._app.add_handler(MessageHandler(filters.TEXT, handle_message.handle))

    @property
    def app(self):
        return self._app

    async def start(self) -> None:
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling()  # type: ignore

    async def stop(self) -> None:
        await self._app.updater.stop()  # type: ignore
        await self._app.stop()
        await self._app.shutdown()
