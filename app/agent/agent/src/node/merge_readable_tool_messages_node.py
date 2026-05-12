from logging import Logger

from agent.agent.src.state.agent_state import (
    AgentState,
    ExecutedToolsState,
    MergeReadableToolMessagesAction,
)
from agent.agent.src.state.unexpected_state_error import UnexpectedStateError


class MergeReadableToolMessagesNode:
    def __init__(self, logger: Logger):
        self._logger = logger

    async def merge(self, agent_state: AgentState) -> dict:
        state = agent_state["state"]

        if not isinstance(state, ExecutedToolsState):
            raise UnexpectedStateError(expected=ExecutedToolsState, actual=state)

        return {
            "state": MergeReadableToolMessagesAction(
                readable_tool_messages=state.readable_tool_messages,
            ),
        }
