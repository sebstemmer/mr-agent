from logging import Logger

from langchain_core.messages import AIMessage, ToolMessage

from agent.tasks.tasks_state import (
    ExecuteToolCallsState,
    FinishExecuteToolCallsAction,
    TasksState,
    get_tasks_substate,
    reduce_execute_tool_calls_with_finish_execute_tool_calls,
)


class LeaveTasksNode:
    def __init__(self, logger: Logger):
        self._logger = logger

    async def execute(self, state: TasksState) -> dict:
        tasks_substate = get_tasks_substate(
            state=state, expected_type=ExecuteToolCallsState
        )
        tool_call = tasks_substate.current_tool_call

        return {
            "messages": [
                ToolMessage(
                    content="Left tasks branch.",
                    tool_call_id=tool_call["id"],
                ),
            ],
            "tasks_substate": reduce_execute_tool_calls_with_finish_execute_tool_calls(
                _state=tasks_substate,
                action=FinishExecuteToolCallsAction(
                    message=AIMessage(content="Left tasks branch."),
                ),
                logger=self._logger,
            ),
            "current_branch": None,
        }
