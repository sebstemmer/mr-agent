from datetime import date
from logging import Logger

from langchain_core.tools import BaseTool
from utils.common.src.llm_builder import LlmBuilder

from agent.agent.src.state.agent_state import AgentState, ExecuteToolCallsAction
from agent.agent.src.state.dispatch_respond_with_text_action import (
    DispatchRespondWithTextAction,
)
from agent.agent.src.tool_registry import ToolRegistry


class PlannerNode:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        tools: list[BaseTool],
        tool_registry: ToolRegistry,
        logger: Logger,
        dispatch_respond_with_text_action: DispatchRespondWithTextAction,
    ):
        non_parallel_tools = [
            name for name, entry in tool_registry.items() if not entry.parallel
        ]

        builder = (
            LlmBuilder(api_key=api_key, model=model)
            .system_prompt(system_prompt, today=lambda: date.today().isoformat())
            .tools(tools=tools, tool_choice="auto", parallel_tool_calls=True)
        )

        if non_parallel_tools:
            builder.instruction(
                f"These tools must be called alone, never in parallel with other tools: "
                f"{', '.join(non_parallel_tools)}."
            )

        self._llm = builder.build()
        self._tool_registry = tool_registry
        self._logger = logger
        self._dispatch_respond_with_text_action = dispatch_respond_with_text_action

    async def plan(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        response = await self._llm.ainvoke(messages=state.messages)

        if response.tool_calls:
            has_non_parallel = any(
                not self._tool_registry[call["name"]].parallel
                for call in response.tool_calls
            )
            if has_non_parallel and len(response.tool_calls) > 1:
                return {
                    "state": await self._dispatch_respond_with_text_action.dispatch(
                        text="Something went wrong, please try again.",
                    ),
                }

            return {
                "state": ExecuteToolCallsAction(
                    message=response,
                    calls=response.tool_calls,
                )
            }
        else:
            return {
                "state": await self._dispatch_respond_with_text_action.dispatch(
                    text=response.content,
                ),
            }
