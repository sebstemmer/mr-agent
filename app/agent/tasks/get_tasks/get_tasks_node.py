from logging import Logger

from agent.tasks.get_tasks.get_tasks_tool import GetTasksInput, GetTasksTool
from agent.tasks.tasks_state import (
    AppendHumanToolResponseToResponsesAction,
    ExecuteToolCallsState,
    TasksState,
    get_tasks_substate,
    reduce_execute_tool_calls_with_append_human_tool_response_to_responses,
)


class GetTasksNode:
    def __init__(self, get_tasks_tool: GetTasksTool, logger: Logger):
        self._get_tasks_tool = get_tasks_tool
        self._logger = logger

    async def execute(self, state: TasksState) -> dict:
        tasks_substate = get_tasks_substate(
            state=state, expected_type=ExecuteToolCallsState
        )
        tool_call = tasks_substate.current_tool_call
        args = GetTasksInput(**tool_call["args"])

        tool_message = await self._get_tasks_tool.arun(
            tool_input=args.model_dump(),
            tool_call_id=tool_call["id"],
        )

        return {
            "messages": [tool_message],
            "tasks_substate": reduce_execute_tool_calls_with_append_human_tool_response_to_responses(
                state=tasks_substate,
                action=AppendHumanToolResponseToResponsesAction(
                    response=tool_message.artifact
                ),
                logger=self._logger,
            ),
        }
