from logging import Logger

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.messages.tool import ToolCall
from utils.common.src.llm_with_system_prompt import LlmWithSystemPrompt

from agent.tasks.chat_about_tasks.chat_about_tasks_tool import (
    _TOOL_NAME as _CHAT_ABOUT_TASKS,
)
from agent.tasks.chat_about_tasks.chat_about_tasks_tool import (
    ChatAboutTasksTool,
)
from agent.tasks.complete_task.complete_task_tool import CompleteTaskTool
from agent.tasks.create_task.create_task_tool import CreateTaskTool
from agent.tasks.delete_task.delete_task_tool import DeleteTaskTool
from agent.tasks.get_tasks.get_tasks_tool import GetTasksTool
from agent.tasks.tasks_state import (
    ExecuteNextToolAction,
    ExecuteToolCallsState,
    FinishExecuteToolCallsAction,
    InitExecuteToolCallsAction,
    TasksState,
    reduce_execute_tool_calls_with_execute_next_tool,
    reduce_execute_tool_calls_with_finish_execute_tool_calls,
    reduce_none_with_init_execute_tool_calls,
)
from agent.tasks.update_task.update_task_tool import UpdateTaskTool


class TasksRouterNode:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        create_task_tool: CreateTaskTool,
        get_tasks_tool: GetTasksTool,
        update_task_tool: UpdateTaskTool,
        complete_task_tool: CompleteTaskTool,
        delete_task_tool: DeleteTaskTool,
        chat_about_tasks_tool: ChatAboutTasksTool,
        branch_name: str,
        logger: Logger,
    ):
        self._branch_name = branch_name
        self._logger = logger
        self._llm = LlmWithSystemPrompt(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            tools=[
                create_task_tool,
                get_tasks_tool,
                update_task_tool,
                complete_task_tool,
                delete_task_tool,
                chat_about_tasks_tool,
            ],
            tool_choice="required",
            parallel_tool_calls=True,
            additional_instructions=None,
        )

    async def route(self, state: TasksState) -> dict:
        tasks_substate = state.get("tasks_substate")

        if tasks_substate is None:
            return await self._invoke_llm(messages=state["messages"])

        if (
            isinstance(tasks_substate, ExecuteToolCallsState)
            and len(tasks_substate.pending_tool_calls) > 0
        ):
            return {
                "tasks_substate": reduce_execute_tool_calls_with_execute_next_tool(
                    state=tasks_substate,
                    _action=ExecuteNextToolAction(),
                    logger=self._logger,
                )
            }

        if isinstance(tasks_substate, ExecuteToolCallsState):
            combined = "\n".join(tasks_substate.human_tool_responses)
            return {
                "tasks_substate": reduce_execute_tool_calls_with_finish_execute_tool_calls(
                    _state=tasks_substate,
                    action=FinishExecuteToolCallsAction(
                        message=AIMessage(content=combined),
                    ),
                    logger=self._logger,
                ),
            }

        raise ValueError(f"Unexpected tasks_substate: {type(tasks_substate).__name__}")

    _TERMINAL_TOOLS = {_CHAT_ABOUT_TASKS}

    _ADDITIONAL_INSTRUCTIONS = ""

    def _truncate_at_terminal_tool(self, tool_calls: list[ToolCall]) -> list[ToolCall]:
        for i, tc in enumerate(tool_calls):
            if tc["name"] in self._TERMINAL_TOOLS:
                truncated = tool_calls[i + 1 :]
                if truncated:
                    self._logger.warning(
                        "[branch=%s] truncated tool_calls after terminal tool '%s': %s",
                        self._branch_name,
                        tc["name"],
                        [t["name"] for t in truncated],
                    )
                return tool_calls[: i + 1]
        return tool_calls

    async def _invoke_llm(self, messages: list[BaseMessage]) -> dict:
        self._logger.info("[branch=%s] handling", self._branch_name)
        response = await self._llm.ainvoke(messages=messages)

        self._logger.info(
            "[branch=%s] tool_calls=%s",
            self._branch_name,
            [tc["name"] for tc in response.tool_calls],
        )

        tool_calls = self._truncate_at_terminal_tool(
            tool_calls=response.tool_calls,
        )
        skipped_messages = [
            ToolMessage(content="Skipped.", tool_call_id=tc["id"])
            for tc in response.tool_calls[len(tool_calls) :]
        ]

        # noinspection PyTypeChecker
        return {
            "messages": [response] + skipped_messages,
            "tasks_substate": reduce_none_with_init_execute_tool_calls(
                _state=None,
                action=InitExecuteToolCallsAction(
                    pending_tool_calls=tool_calls[1:],
                    current_tool_call=tool_calls[0],
                ),
                logger=self._logger,
            ),
        }
