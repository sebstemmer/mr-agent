from logging import Logger

from langchain_core.messages import ToolMessage

from agent.tasks.chat_about_tasks.chat_about_tasks_tool import ChatAboutTasksInput
from agent.tasks.tasks_state import (
    AppendHumanToolResponseToResponsesAction,
    ExecuteToolCallsState,
    TasksState,
    get_tasks_substate,
    reduce_execute_tool_calls_with_append_human_tool_response_to_responses,
)


class ChatAboutTasksNode:
    def __init__(self, logger: Logger):
        self._logger = logger

    async def execute(self, state: TasksState) -> dict:
        tasks_substate = get_tasks_substate(
            state=state, expected_type=ExecuteToolCallsState
        )
        tool_call = tasks_substate.current_tool_call
        args = ChatAboutTasksInput(**tool_call["args"])

        return {
            "messages": [
                ToolMessage(
                    content=args.message,
                    tool_call_id=tool_call["id"],
                ),
            ],
            "tasks_substate": reduce_execute_tool_calls_with_append_human_tool_response_to_responses(
                state=tasks_substate,
                action=AppendHumanToolResponseToResponsesAction(
                    response=args.message
                ),
                logger=self._logger,
            ),
        }
