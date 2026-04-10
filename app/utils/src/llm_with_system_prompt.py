from datetime import date

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI


class LlmWithSystemPrompt:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        tools: list[BaseTool],
        tool_choice: str,
    ):
        self._system_prompt = system_prompt
        # noinspection PyTypeChecker
        llm = ChatOpenAI(api_key=api_key, model=model)
        self._bound_llm = llm.bind_tools(tools, tool_choice=tool_choice)

    async def ainvoke(self, messages: list[BaseMessage]) -> AIMessage:
        today = date.today().isoformat()
        system_message = SystemMessage(content=self._system_prompt.format(today=today))
        return await self._bound_llm.ainvoke([system_message] + messages)
