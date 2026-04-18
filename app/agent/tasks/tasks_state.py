from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TypeVar

from langchain_core.messages import AIMessage
from langchain_core.messages.tool import ToolCall

from agent.state.agent_state import AgentState


@dataclass
class _TasksSubStateInterface:
    pass


@dataclass
class ExecuteToolCallsState(_TasksSubStateInterface):
    pending_tool_calls: list[ToolCall]
    current_tool_call: ToolCall
    human_tool_responses: list[str]


@dataclass
class RespondWithTextState(_TasksSubStateInterface):
    message: AIMessage


@dataclass
class _TasksActionInterface:
    pass


@dataclass
class AppendHumanToolResponseToResponsesAction(_TasksActionInterface):
    response: str


@dataclass
class ExecuteNextToolAction(_TasksActionInterface):
    pass


@dataclass
class InitExecuteToolCallsAction(_TasksActionInterface):
    pending_tool_calls: list[ToolCall]
    current_tool_call: ToolCall


@dataclass
class InitRespondWithTextAction(_TasksActionInterface):
    message: AIMessage


@dataclass
class FinishExecuteToolCallsAction(_TasksActionInterface):
    message: AIMessage


@dataclass
class ResetToNoneAction(_TasksActionInterface):
    pass


RouterState = ExecuteToolCallsState | RespondWithTextState | None


def reduce_none_with_init_execute_tool_calls(
    _state: None,
    action: InitExecuteToolCallsAction,
    logger: logging.Logger,
) -> ExecuteToolCallsState:
    logger.info("None + InitExecuteToolCallsAction -> ExecuteToolCallsState")
    logger.debug("state=%s action=%s", _state, action)
    return ExecuteToolCallsState(
        pending_tool_calls=action.pending_tool_calls,
        current_tool_call=action.current_tool_call,
        human_tool_responses=[],
    )


def reduce_none_with_init_respond_with_text(
    _state: None,
    action: InitRespondWithTextAction,
    logger: logging.Logger,
) -> RespondWithTextState:
    logger.info("None + InitRespondWithTextAction -> RespondWithTextState")
    logger.debug("state=%s action=%s", _state, action)
    return RespondWithTextState(message=action.message)


def reduce_respond_with_text_with_reset_to_none(
    _state: RespondWithTextState,
    _action: ResetToNoneAction,
    logger: logging.Logger,
) -> None:
    logger.info("RespondWithTextState + ResetToNoneAction -> None")
    logger.debug("state=%s action=%s", _state, _action)
    return None


def reduce_execute_tool_calls_with_finish_execute_tool_calls(
    _state: ExecuteToolCallsState,
    action: FinishExecuteToolCallsAction,
    logger: logging.Logger,
) -> RespondWithTextState:
    logger.info("ExecuteToolCallsState + FinishExecuteToolCallsAction -> RespondWithTextState")
    logger.debug("state=%s action=%s", _state, action)
    return RespondWithTextState(message=action.message)


def reduce_execute_tool_calls_with_append_human_tool_response_to_responses(
    state: ExecuteToolCallsState,
    action: AppendHumanToolResponseToResponsesAction,
    logger: logging.Logger,
) -> ExecuteToolCallsState:
    logger.info("ExecuteToolCallsState + AppendHumanToolResponseToResponsesAction -> ExecuteToolCallsState")
    logger.debug("state=%s action=%s", state, action)
    return ExecuteToolCallsState(
        pending_tool_calls=state.pending_tool_calls,
        current_tool_call=state.current_tool_call,
        human_tool_responses=state.human_tool_responses + [action.response],
    )


def reduce_execute_tool_calls_with_execute_next_tool(
    state: ExecuteToolCallsState,
    _action: ExecuteNextToolAction,
    logger: logging.Logger,
) -> ExecuteToolCallsState:
    logger.info("ExecuteToolCallsState + ExecuteNextToolAction -> ExecuteToolCallsState")
    logger.debug("state=%s action=%s", state, _action)
    # noinspection PyTypeChecker
    return ExecuteToolCallsState(
        pending_tool_calls=state.pending_tool_calls[1:],
        current_tool_call=state.pending_tool_calls[0],
        human_tool_responses=state.human_tool_responses,
    )


class TasksState(AgentState):
    tasks_substate: _TasksSubStateInterface


_T = TypeVar("_T", bound=_TasksSubStateInterface)


def get_tasks_substate(state: TasksState, expected_type: type[_T]) -> _T:
    tasks_substate = state["tasks_substate"]
    if not isinstance(tasks_substate, expected_type):
        raise ValueError(
            f"Expected {expected_type.__name__}, got {type(tasks_substate).__name__}"
        )
    return tasks_substate


def clear_subgraph_state(state: TasksState) -> dict:
    return {
        "messages": state["messages"],
        "current_branch": state["current_branch"],
        "router_state": None,
    }
