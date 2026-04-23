from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

from agent.common.sequential_tool_execution_state import (
    SequentialToolExecutionState,
    SequentialToolExecutionStateType,
    parse_sequential_tool_execution_state,
)

SEQUENTIAL_TOOL_EXECUTION_STATE_KEY = "sequential_tool_execution_state"


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    sequential_tool_execution_state: SequentialToolExecutionState


def get_sequential_tool_execution_state(
    state: AgentState, expected_type: type[SequentialToolExecutionStateType]
) -> SequentialToolExecutionStateType:
    return parse_sequential_tool_execution_state(
        sequential_tool_execution_state=get_sequential_tool_execution_state_or_none(
            state=state,
        ),
        expected_type=expected_type,
    )


def get_sequential_tool_execution_state_or_none(
    state: AgentState,
) -> SequentialToolExecutionState | None:
    return state.get(SEQUENTIAL_TOOL_EXECUTION_STATE_KEY)
