from typing import Protocol


class MessageSender(Protocol):
    async def send(self, message: str) -> None: ...
