from datetime import date

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI

_SYSTEM_PROMPT = (
    "You are a helpful assistant. Today's date is {today}. "
    "When a tool returns formatted data, present it to the user exactly as-is "
    "without rephrasing or summarizing."
)


class HandleConversation:
    def __init__(self, api_key: str, model: str):
        # noinspection PyTypeChecker
        self._llm = ChatOpenAI(api_key=api_key, model=model)

    async def handle(self, messages: list[BaseMessage]) -> BaseMessage:
        system = SystemMessage(content=_SYSTEM_PROMPT.format(today=date.today()))
        return await self._llm.ainvoke([system] + messages)
