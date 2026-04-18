from logging import Logger

from agent.tasks.create_task.create_task_tool import CreateTaskInput, CreateTaskTool
from agent.tasks.tasks_state import (
    AppendHumanToolResponseToResponsesAction,
    ExecuteToolCallsState,
    TasksState,
    get_tasks_substate,
    reduce_execute_tool_calls_with_append_human_tool_response_to_responses,
)


class CreateTaskNode:
    def __init__(self, create_task_tool: CreateTaskTool, logger: Logger):
        self._create_task_tool = create_task_tool
        self._logger = logger

    async def execute(self, state: TasksState) -> dict:
        tasks_substate = get_tasks_substate(
            state=state, expected_type=ExecuteToolCallsState
        )
        tool_call = tasks_substate.current_tool_call
        args = CreateTaskInput(**tool_call["args"])

        tool_message = await self._create_task_tool.arun(
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
