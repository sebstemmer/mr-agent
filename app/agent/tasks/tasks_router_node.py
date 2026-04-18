from logging import Logger

from langchain_core.messages import AIMessage, BaseMessage
from utils.common.src.llm_with_system_prompt import LlmWithSystemPrompt

from agent.tasks.complete_task.complete_task_tool import CompleteTaskTool
from agent.tasks.create_task.create_task_tool import CreateTaskTool
from agent.tasks.delete_task.delete_task_tool import DeleteTaskTool
from agent.tasks.get_tasks.get_tasks_tool import GetTasksTool
from agent.tasks.leave_tasks.leave_tasks_tool import LeaveTasksTool
from agent.tasks.tasks_state import (
    ExecuteNextToolAction,
    ExecuteToolCallsState,
    FinishExecuteToolCallsAction,
    InitExecuteToolCallsAction,
    InitRespondWithTextAction,
    TasksState,
    reduce_execute_tool_calls_with_execute_next_tool,
    reduce_execute_tool_calls_with_finish_execute_tool_calls,
    reduce_none_with_init_execute_tool_calls,
    reduce_none_with_init_respond_with_text,
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
        leave_tasks_tool: LeaveTasksTool,
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
                leave_tasks_tool,
            ],
            tool_choice="auto",
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

    async def _invoke_llm(self, messages: list[BaseMessage]) -> dict:
        self._logger.info("[branch=%s] handling", self._branch_name)
        response = await self._llm.ainvoke(messages=messages)

        if not response.tool_calls:
            self._logger.info("[branch=%s] text response", self._branch_name)
            return {
                "messages": [response],
                "tasks_substate": reduce_none_with_init_respond_with_text(
                    _state=None,
                    action=InitRespondWithTextAction(message=response),
                    logger=self._logger,
                ),
            }

        self._logger.info(
            "[branch=%s] tool_calls=%s",
            self._branch_name,
            [tc["name"] for tc in response.tool_calls],
        )

        # noinspection PyTypeChecker
        return {
            "messages": [response],
            "tasks_substate": reduce_none_with_init_execute_tool_calls(
                _state=None,
                action=InitExecuteToolCallsAction(
                    pending_tool_calls=response.tool_calls[1:],
                    current_tool_call=response.tool_calls[0],
                ),
                logger=self._logger,
            ),
        }
