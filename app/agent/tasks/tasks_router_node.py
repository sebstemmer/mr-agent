from logging import Logger

from langchain_core.tools import BaseTool
from utils.common.src.llm_with_system_prompt import LlmWithSystemPrompt

from agent.common.sequential_tool_execution_state import (
    init_execute_tool_calls_or_respond_with_text,
    invoke_llm_execute_next_tool_or_finish_tool_execution,
)
from agent.tasks.tasks_state import (
    TASKS_SEQUENTIAL_TOOL_EXECUTION_STATE_KEY,
    TasksState,
    get_tasks_sequential_tool_execution_state_or_none,
)


class TasksRouterNode:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        tools: list[BaseTool],
        branch_name: str,
        logger: Logger,
    ):
        self._branch_name = branch_name
        self._logger = logger
        self._llm = LlmWithSystemPrompt(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=True,
            additional_instructions=[
                "You are only responsible for the user's personal task list."
                " Ignore anything unrelated to personal tasks."
            ],
        )

    async def route(self, state: TasksState) -> dict:
        return await invoke_llm_execute_next_tool_or_finish_tool_execution(
            substate=get_tasks_sequential_tool_execution_state_or_none(tasks_state=state),
            state_key=TASKS_SEQUENTIAL_TOOL_EXECUTION_STATE_KEY,
            invoke_llm=lambda: init_execute_tool_calls_or_respond_with_text(
                llm=self._llm,
                messages=state["messages"],
                state_key=TASKS_SEQUENTIAL_TOOL_EXECUTION_STATE_KEY,
                logger=self._logger,
                label=self._branch_name,
            ),
            logger=self._logger,
        )
