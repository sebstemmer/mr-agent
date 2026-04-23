from logging import Logger

from agent.common.sequential_tool_execution_state import (
    ResetToNoneAction,
    RespondWithTextState,
    parse_sequential_tool_execution_state,
    reduce_respond_with_text_with_reset_to_none,
)


class TextResponseNode:
    def __init__(self, state_key: str, logger: Logger):
        self._state_key = state_key
        self._logger = logger

    async def execute(self, state: dict) -> dict:
        respond_with_text_state = parse_sequential_tool_execution_state(
            sequential_tool_execution_state=state[self._state_key],
            expected_type=RespondWithTextState,
        )
        return {
            "messages": [respond_with_text_state.message],
            self._state_key: reduce_respond_with_text_with_reset_to_none(
                _state=respond_with_text_state,
                _action=ResetToNoneAction(),
                logger=self._logger,
            ),
        }
