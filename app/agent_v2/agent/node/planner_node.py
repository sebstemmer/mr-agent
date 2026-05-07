from datetime import date
from logging import Logger

from langchain_core.tools import BaseTool
from utils.common.src.llm_builder import LlmBuilder

from agent_v2.agent.state.agent_state import AgentState, ExecuteToolCallsAction
from agent_v2.agent.state.dispatch_respond_with_text_action import (
    DispatchRespondWithTextAction,
)


class PlannerNode:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        tools: list[BaseTool],
        logger: Logger,
        dispatch_respond_with_text_action: DispatchRespondWithTextAction,
    ):
        self._llm = (
            LlmBuilder(api_key=api_key, model=model)
            .system_prompt(system_prompt, today=lambda: date.today().isoformat())
            .tools(tools=tools, tool_choice="auto", parallel_tool_calls=True)
            .build()
        )
        self._logger = logger
        self._dispatch_respond_with_text_action = dispatch_respond_with_text_action

    async def plan(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        response = await self._llm.ainvoke(messages=state.messages)

        if response.tool_calls:
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
