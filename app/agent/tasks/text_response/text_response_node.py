from logging import Logger

from agent.tasks.tasks_state import (
    ResetToNoneAction,
    RespondWithTextState,
    TasksState,
    get_tasks_substate,
    reduce_respond_with_text_with_reset_to_none,
)


class TextResponseNode:
    def __init__(self, logger: Logger):
        self._logger = logger

    async def execute(self, state: TasksState) -> dict:
        tasks_substate = get_tasks_substate(state=state, expected_type=RespondWithTextState)
        return {
            "messages": [tasks_substate.message],
            "tasks_substate": reduce_respond_with_text_with_reset_to_none(
                _state=tasks_substate,
                _action=ResetToNoneAction(),
                logger=self._logger,
            ),
        }
