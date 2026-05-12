from collections.abc import Callable
from typing import TypeVar

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

_T = TypeVar("_T", bound=BaseModel)


class Llm:
    def __init__(
        self,
        llm,
        structured_llm,
        system_prompt: str | None,
        system_prompt_variables: dict[str, Callable[[], str]],
        instructions: list[str],
    ):
        self._llm = llm
        self._structured_llm = structured_llm
        self._system_prompt = system_prompt
        self._system_prompt_variables = system_prompt_variables
        self._instructions = instructions

    def _build_messages(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        if self._system_prompt is not None:
            resolved = {k: v() for k, v in self._system_prompt_variables.items()}
            content = self._system_prompt.format(**resolved) if resolved else self._system_prompt
            content += "".join(f" {i}" for i in self._instructions)
            return [SystemMessage(content=content)] + messages
        return messages

    async def ainvoke(self, messages: list[BaseMessage]) -> AIMessage:
        return await self._llm.ainvoke(self._build_messages(messages=messages))

    async def ainvoke_structured(self, messages: list[BaseMessage]) -> _T:
        return await self._structured_llm.ainvoke(self._build_messages(messages=messages))


class LlmBuilder:
    def __init__(self, api_key: str, model: str):
        self._api_key = api_key
        self._model = model
        self._system_prompt: str | None = None
        self._system_prompt_variables: dict[str, Callable[[], str]] = {}
        self._instructions: list[str] = []
        self._tools: list[BaseTool] | None = None
        self._tool_choice: str | None = None
        self._parallel_tool_calls: bool | None = None
        self._structured_output: type[BaseModel] | None = None

    def tools(
        self,
        tools: list[BaseTool],
        tool_choice: str,
        parallel_tool_calls: bool,
    ) -> "LlmBuilder":
        self._tools = tools
        self._tool_choice = tool_choice
        self._parallel_tool_calls = parallel_tool_calls
        return self

    def structured_output(self, schema: type[BaseModel]) -> "LlmBuilder":
        self._structured_output = schema
        return self

    def instruction(self, instruction: str) -> "LlmBuilder":
        self._instructions.append(instruction)
        return self

    def system_prompt(
        self, system_prompt: str, **variables: Callable[[], str]
    ) -> "LlmBuilder":
        self._system_prompt = system_prompt
        self._system_prompt_variables = variables
        return self

    def build(self) -> Llm:
        # noinspection PyTypeChecker
        llm = ChatOpenAI(api_key=self._api_key, model=self._model)
        if self._tools:
            llm = llm.bind_tools(
                self._tools,
                tool_choice=self._tool_choice,
                parallel_tool_calls=self._parallel_tool_calls,
            )
        structured_llm = (
            llm.with_structured_output(self._structured_output)
            if self._structured_output
            else None
        )
        return Llm(
            llm=llm,
            structured_llm=structured_llm,
            system_prompt=self._system_prompt,
            system_prompt_variables=self._system_prompt_variables,
            instructions=self._instructions,
        )
