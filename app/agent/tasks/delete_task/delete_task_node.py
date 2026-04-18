from logging import Logger

from langchain_core.messages import ToolMessage
from utils.common.src.confirm import confirm

from agent.tasks.delete_task.delete_task_tool import DeleteTaskInput, DeleteTaskTool
from agent.tasks.tasks_state import (
    AppendHumanToolResponseToResponsesAction,
    ExecuteToolCallsState,
    TasksState,
    get_tasks_substate,
    reduce_execute_tool_calls_with_append_human_tool_response_to_responses,
)


class DeleteTaskNode:
    def __init__(self, delete_task_tool: DeleteTaskTool, logger: Logger):
        self._delete_task_tool = delete_task_tool
        self._logger = logger

    async def execute(self, state: TasksState) -> dict:
        tasks_substate = get_tasks_substate(
            state=state, expected_type=ExecuteToolCallsState
        )
        tool_call = tasks_substate.current_tool_call
        args = DeleteTaskInput(**tool_call["args"])

        if not confirm(question=f"Delete task '{args.title}'?"):
            return {
                "messages": [
                    ToolMessage(
                        content=f"User declined deletion of task {args.task_id}.",
                        tool_call_id=tool_call["id"],
                    ),
                ],
                "tasks_substate": reduce_execute_tool_calls_with_append_human_tool_response_to_responses(
                    state=tasks_substate,
                    action=AppendHumanToolResponseToResponsesAction(
                        response=f"Deletion of '{args.title}' declined."
                    ),
                    logger=self._logger,
                ),
            }

        tool_message = await self._delete_task_tool.arun(
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
