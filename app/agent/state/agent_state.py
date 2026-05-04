import logging
import operator
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel

from agent.common.parallel_tool_execution_state import (
    ParallelToolExecutionState,
    reduce_parallel_tool_execution_state,
)
from agent.common.sequential_tool_execution_state import (
    SequentialToolExecutionState,
    SequentialToolExecutionStateType,
    parse_sequential_tool_execution_state,
)
from agent.job_search.src.handle_job_search_node import JOB_SEARCH_BRANCH
from agent.tasks.create_tasks_subgraph import PERSONAL_TASK_LIST_BRANCH
from agent.weather.src.handle_weather_node import HANDLE_WEATHER_NODE_NAME

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


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    sequential_tool_execution_state: SequentialToolExecutionState
    tool_execution_state: Annotated[
        ParallelToolExecutionState, reduce_parallel_tool_execution_state
    ]
    active_branches: list[str]
    orchestrator_decision_state: Annotated[
        OrchestratorDecisionState | None, reduce_orchestrator_decision_state
    ]
    branch_results: Annotated[list[BranchResult], operator.add]


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
