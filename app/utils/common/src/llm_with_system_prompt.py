from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from utils.common.src.datetime_utils import today_berlin


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

    async def ainvoke(
        self,
        messages: list[BaseMessage],
        additional_instructions: list[str] | None = None,
    ) -> AIMessage:
        today = today_berlin().isoformat()
        content = self._system_prompt.format(today=today)
        content += "".join(f" {i}" for i in additional_instructions or [])
        system_message = SystemMessage(content=content)
        return await self._bound_llm.ainvoke([system_message] + messages)
