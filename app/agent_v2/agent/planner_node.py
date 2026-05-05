from logging import Logger

from langchain_core.tools import BaseTool
from utils.common.src.llm_builder import LlmBuilder

from agent_v2.agent.agent_state import (
    AgentState,
    ExecuteToolCallsAction,
    RespondWithTextAction,
)


class PlannerNode:
    def __init__(
        self,
        api_key: str,
        model: str,
        tools: list[BaseTool],
        logger: Logger,
    ):
        self._llm = (
            LlmBuilder(api_key=api_key, model=model)
            .tools(tools=tools, tool_choice="auto", parallel_tool_calls=True)
            .build()
        )
        self._logger = logger

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
                "state": RespondWithTextAction(
                    message=response,
                ),
            }
