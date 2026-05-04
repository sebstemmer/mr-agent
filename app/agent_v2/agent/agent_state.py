import logging
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, TypedDict

from agent.common.sequential_tool_execution_state import (
    SequentialToolExecutionState,
    SequentialToolExecutionStateType,
    parse_sequential_tool_execution_state,
)
from agent.job_search.src.handle_job_search_node import JOB_SEARCH_BRANCH
from agent.tasks.create_tasks_subgraph import PERSONAL_TASK_LIST_BRANCH
from agent.weather.src.handle_weather_node import HANDLE_WEATHER_NODE_NAME
from langchain_core.messages import BaseMessage
from langchain_core.messages.tool import ToolCall
from langgraph.graph import add_messages
from pydantic import BaseModel

SEQUENTIAL_TOOL_EXECUTION_STATE_KEY = "sequential_tool_execution_state"


class Branch(str, Enum):
    WEATHER = HANDLE_WEATHER_NODE_NAME
    JOB_SEARCH = JOB_SEARCH_BRANCH
    PERSONAL_TASK_LIST = PERSONAL_TASK_LIST_BRANCH


class OrchestratorDecisionState(BaseModel):
    pass


class TextResponseState(OrchestratorDecisionState):
    text_response: str


class ExecuteBranchesState(OrchestratorDecisionState):
    branches: list[Branch]


@dataclass
class _OrchestratorDecisionAction:
    logger: logging.Logger


@dataclass
class DecidedForTextResponseAction(_OrchestratorDecisionAction):
    text_response: str


@dataclass
class DecidedForBranchesAction(_OrchestratorDecisionAction):
    branches: list[Branch]


@dataclass
class ResetStateAction(_OrchestratorDecisionAction):
    pass


def reduce_orchestrator_decision_state(
    state: OrchestratorDecisionState | None, action: _OrchestratorDecisionAction
) -> OrchestratorDecisionState | None:
    action.logger.debug("state=%s action=%s", state, action)

    if isinstance(action, DecidedForTextResponseAction):
        action.logger.info("DecidedForTextResponseAction -> TextResponseState")
        return TextResponseState(text_response=action.text_response)

    if isinstance(action, DecidedForBranchesAction):
        action.logger.info("DecidedForBranchesAction -> ExecuteBranchesState")
        return ExecuteBranchesState(branches=action.branches)

    if isinstance(action, ResetStateAction):
        action.logger.info("ResetStateAction -> None")
        return None

    raise ValueError(f"Unhandled action: {type(action).__name__}")


@dataclass
class BranchResult:
    branch: Branch
    visible_result: str


@dataclass
class DisplayableMessagesState:
    messages: list[str]


@dataclass
class _DisplayableMessagesAction:
    pass


@dataclass
class ToolCallsState:
    pass


@dataclass
class ExecuteToolCallsState(ToolCallsState):
    calls: list[ToolCall]


@dataclass
class _ToolCallsAction:
    logger: logging.Logger


@dataclass
class ExecuteToolCallsAction(_ToolCallsAction):
    calls: list[ToolCall]


def reduce_displayable_messages_state(
    state: DisplayableMessagesState, action: _DisplayableMessagesAction
) -> list[BaseMessage]:
    pass


def reduce_tool_calls_state(
    state: ToolCallsState | None, action: _ToolCallsAction
) -> ToolCallsState | None:
    action.logger.debug("state=%s action=%s", state, action)

    if state is None and isinstance(action, ExecuteToolCallsAction):
        action.logger.info("None + ExecuteToolCallsAction -> ExecuteToolCallsState")
        return ExecuteToolCallsState(calls=action.calls)

    raise ValueError(
        f"Unhandled state/action: {type(state).__name__} + {type(action).__name__}"
    )


@dataclass
class ToolState:
    logger: logging.Logger


@dataclass
class ExecuteToolState(ToolState):
    call: ToolCall


@dataclass
class _ToolAction:
    logger: logging.Logger


@dataclass
class ExecuteToolAction(_ToolAction):
    call: ToolCall


def reduce_tool_state(state: ToolState | None, action: _ToolAction) -> ToolState | None:
    action.logger.debug("state=%s action=%s", state, action)

    if state is None and isinstance(action, ExecuteToolAction):
        action.logger.info("None + ExecuteToolAction -> ExecuteToolState")
        return ExecuteToolState(logger=action.logger, call=action.call)

    raise ValueError(
        f"Unhandled state/action: {type(state).__name__} + {type(action).__name__}"
    )


@dataclass
class State:
    logger: logging.Logger


@dataclass
class _Action:
    logger: logging.Logger


class AddMessageAction(_Action):
    pass


@dataclass
def reduce(state: ToolState | None, action: _ToolAction) -> ToolState | None:
    action.logger.debug("state=%s action=%s", state, action)

    if state is None and isinstance(action, ExecuteToolAction):
        action.logger.info("None + ExecuteToolAction -> ExecuteToolState")
        return ExecuteToolState(logger=action.logger, call=action.call)

    raise ValueError(
        f"Unhandled state/action: {type(state).__name__} + {type(action).__name__}"
    )


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    displayable_messages_state: Annotated[
        DisplayableMessagesState, reduce_displayable_messages_state
    ]
    tool_calls_state: Annotated[ToolCallsState, reduce_tool_calls_state]
    tool_state: Annotated[ToolState, reduce_tool_state]
    big_state: Annotated[State]


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
