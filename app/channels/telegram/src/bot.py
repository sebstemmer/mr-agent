from channels.telegram.src.handle_telegram_init import HandleTelegramInit
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)


class TelegramBot:
    def __init__(self, token: str, handle_init: HandleTelegramInit):
        self._app = (
            ApplicationBuilder()
            .token(token)
            .read_timeout(30)
            .write_timeout(30)
            .build()
        )
        self._app.add_handler(CommandHandler("init", handle_init.handle))

    @property
    def app(self):
        return self._app

    async def start(self) -> None:
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling()

    async def stop(self) -> None:
        await self._app.updater.stop()
        await self._app.stop()
        await self._app.shutdown()
