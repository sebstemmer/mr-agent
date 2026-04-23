from logging import Logger

from langchain_core.messages import ToolMessage
from utils.common.src.confirm import confirm

from agent.common.sequential_tool_execution_state import (
    AppendHumanToolResponseToResponsesAction,
    ExecuteToolCallsState,
    reduce_execute_tool_calls_with_append_human_tool_response_to_responses,
)
from agent.tasks.tasks_state import (
    TASKS_SEQUENTIAL_TOOL_EXECUTION_STATE_KEY,
    TasksState,
    get_tasks_sequential_tool_execution_state,
)
from agent.tasks.update_task.update_task_tool import UpdateTaskInput, UpdateTaskTool


class UpdateTaskNode:
    def __init__(self, update_task_tool: UpdateTaskTool, logger: Logger):
        self._update_task_tool = update_task_tool
        self._logger = logger

    async def execute(self, state: TasksState) -> dict:
        tasks_substate = get_tasks_sequential_tool_execution_state(
            tasks_state=state, expected_type=ExecuteToolCallsState
        )
        tool_call = tasks_substate.current_tool_call
        args = UpdateTaskInput(**tool_call["args"])

        changes = []
        if args.title is not None:
            changes.append(f"title to '{args.title}'")
        if args.due_date is not None:
            changes.append(f"due date to {args.due_date}")
        if args.remove_due_date:
            changes.append("remove due date")

        description = ", ".join(changes)

        if not confirm(question=f"Update task: {description}?"):
            return {
                "messages": [
                    ToolMessage(
                        content=f"User declined update for task {args.task_id}.",
                        tool_call_id=tool_call["id"],
                    ),
                ],
                TASKS_SEQUENTIAL_TOOL_EXECUTION_STATE_KEY: reduce_execute_tool_calls_with_append_human_tool_response_to_responses(
                    state=tasks_substate,
                    action=AppendHumanToolResponseToResponsesAction(
                        response=f"Update declined: {description}."
                    ),
                    logger=self._logger,
                ),
            }

        tool_message = await self._update_task_tool.arun(
            tool_input=args.model_dump(),
            tool_call_id=tool_call["id"],
        )

        return {
            "messages": [tool_message],
            TASKS_SEQUENTIAL_TOOL_EXECUTION_STATE_KEY: reduce_execute_tool_calls_with_append_human_tool_response_to_responses(
                state=tasks_substate,
                action=AppendHumanToolResponseToResponsesAction(
                    response=tool_message.artifact
                ),
                logger=self._logger,
            ),
        }
