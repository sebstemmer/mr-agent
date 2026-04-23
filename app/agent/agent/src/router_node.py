from logging import Logger

from langchain_core.tools import BaseTool
from utils.common.src.llm_with_system_prompt import LlmWithSystemPrompt

from agent.common.sequential_tool_execution_state import (
    init_execute_tool_calls_or_respond_with_text,
    invoke_llm_execute_next_tool_or_finish_tool_execution,
)
from agent.state.agent_state import (
    SEQUENTIAL_TOOL_EXECUTION_STATE_KEY,
    AgentState,
    get_sequential_tool_execution_state_or_none,
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

    async def route(self, state: AgentState) -> dict:
        return await invoke_llm_execute_next_tool_or_finish_tool_execution(
            substate=get_sequential_tool_execution_state_or_none(state=state),
            state_key=SEQUENTIAL_TOOL_EXECUTION_STATE_KEY,
            invoke_llm=lambda: init_execute_tool_calls_or_respond_with_text(
                llm=self._llm,
                messages=state["messages"],
                state_key=SEQUENTIAL_TOOL_EXECUTION_STATE_KEY,
                logger=self._logger,
                label="router",
            ),
            logger=self._logger,
        )
