from logging import Logger

from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool
from utils.common.src.llm_with_system_prompt import LlmWithSystemPrompt

from agent.common.parallel_tool_execution_state import (
    ExecuteToolCallsState,
    ExecutingToolsAction,
    IdxAndToolCall,
    RespondWithTextAction,
)
from agent.state.agent_state import (
    AgentState,
)


class RouterNode:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        tools: list[BaseTool],
        logger: Logger,
    ):
        self._logger = logger
        self._llm = LlmWithSystemPrompt(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=True,
            additional_instructions=None,
        )

    # todo for sebstemmer: handle state call with string
    async def route(self, state: AgentState) -> dict:
        tool_execution_state = state["tool_execution_state"]

        if tool_execution_state is None:
            return await self._invoke_llm(
                state=state,
            )

        if isinstance(tool_execution_state, ExecuteToolCallsState):
            return await self._summarize(execute_tool_calls_state=tool_execution_state)

        raise ValueError(f"tool_execution_state: {type(tool_execution_state).__name__}")

    async def _invoke_llm(self, state: AgentState) -> dict:
        response = await self._llm.ainvoke(messages=state["messages"])

        if not response.tool_calls:
            return {
                "tool_execution_state": RespondWithTextAction(
                    logger=self._logger, message=response
                )
            }
        # todo for sebstemmer: add response
        return {
            "tool_execution_state": ExecutingToolsAction(
                logger=self._logger,
                calls=[
                    IdxAndToolCall(idx=idx, call=call)
                    for idx, call in enumerate(response.tool_calls)
                ],
            )
        }

    async def _summarize(self, execute_tool_calls_state: ExecuteToolCallsState) -> dict:
        combined_message = "\n\n".join(
            [
                message.response
                for message in sorted(
                    execute_tool_calls_state.human_responses, key=lambda m: m.idx
                )
            ]
        )

        return {
            "tool_execution_state": RespondWithTextAction(
                logger=self._logger, message=AIMessage(content=combined_message)
            ),
            "messages": [
                tool_message.message
                for tool_message in sorted(
                    execute_tool_calls_state.tool_messages, key=lambda m: m.idx
                )
            ],
        }
