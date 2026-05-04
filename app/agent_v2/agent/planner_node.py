from logging import Logger

from agent.state.agent_state import (
    AgentState,
)
from utils.common.src.llm_builder import LlmBuilder

from agent_v2.agent.agent_state import ExecuteToolCallsAction


class PlannerNode:
    def __init__(
        self,
        api_key: str,
        model: str,
        logger: Logger,
    ):
        self._llm = LlmBuilder(api_key=api_key, model=model).build()
        self._logger = logger

    async def plan(self, state: AgentState) -> dict:
        response = await self._llm.ainvoke(
            messages=state["messages"],
        )

        if response.tool_calls:
            return {
                "messages": response.content,
                "tool_calls_state": ExecuteToolCallsAction(
                    logger=self._logger, calls=response.tool_calls
                ),
            }
        else:
            # todo for sebstemmer
            pass
