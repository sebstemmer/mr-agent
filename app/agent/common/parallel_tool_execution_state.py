from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.messages.tool import ToolCall, ToolMessage
from langgraph.graph import END
from utils.common.src.llm_with_system_prompt import LlmWithSystemPrompt

from agent.common.sequential_tool_execution_state import SequentialToolExecutionState


@dataclass
class ParallelToolExecutionState:
    pass


@dataclass
class IdxAndToolCall:
    idx: int
    call: ToolCall


@dataclass
class IdxAndHumanResponse:
    idx: int
    response: str


@dataclass
class IdxAndToolMessage:
    idx: int
    message: ToolMessage


@dataclass
class ExecuteToolCallsState(ParallelToolExecutionState):
    calls: list[IdxAndToolCall]
    tool_messages: list[IdxAndToolMessage]
    human_responses: list[IdxAndHumanResponse]


@dataclass
class RespondWithTextState(ParallelToolExecutionState):
    message: AIMessage


@dataclass
class _ActionInterface:
    logger: logging.Logger


@dataclass
class AppendHumanToolResponseToResponsesAction(_ActionInterface):
    response: str


@dataclass
class ExecutingToolsAction(_ActionInterface):
    calls: list[IdxAndToolCall]


@dataclass
class SummarizeToolResultsAction(_ActionInterface):
    pass


@dataclass
class ExecutedToolAction(_ActionInterface):
    response: str


@dataclass
class InitExecuteToolCallsAction(_ActionInterface):
    pending_tool_calls: list[ToolCall]
    current_tool_call: ToolCall


@dataclass
class FinishExecuteToolCallsAction(_ActionInterface):
    message: AIMessage


@dataclass
class ResetToNoneAction(_ActionInterface):
    pass


@dataclass
class RespondWithTextAction(_ActionInterface):
    message: AIMessage


def reduce_parallel_tool_execution_state(
    state: ParallelToolExecutionState | None, action: _ActionInterface
) -> ParallelToolExecutionState | None:
    action.logger.debug("state=%s action=%s", state, action)

    if state is None and isinstance(action, RespondWithTextAction):
        action.logger.info("None + RespondWithTextAction -> RespondWithTextState")
        return RespondWithTextState(
            message=action.message,
        )

    if state is None and isinstance(action, ExecutingToolsAction):
        action.logger.info("None + ExecutingToolsAction -> ExecuteToolCallsState")
        return ExecuteToolCallsState(
            calls=action.calls,
            tool_messages=[],
            human_responses=[],
        )

    if isinstance(state, ExecuteToolCallsState) and isinstance(
        action, SummarizeToolResultsAction
    ):
        action.logger.info(
            "ExecuteToolCallsState + SummarizeToolResultsAction -> RespondWithTextState"
        )
        return RespondWithTextState(
            calls=action.calls,
            tool_messages=[],
            human_responses=[],
        )

    raise ValueError(
        f"Unhandled state/action: {type(state).__name__} + {type(action).__name__}"
    )


def reduce_none_with_respond_with_text(
    _state: None,
    action: RespondWithTextAction,
    logger: logging.Logger,
) -> RespondWithTextState:
    logger.info("None + RespondWithTextAction -> RespondWithTextState")
    logger.debug("state=%s action=%s", _state, action)
    return RespondWithTextState(message=action.message)


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
    logger.info(
        "ExecuteToolCallsState + FinishExecuteToolCallsAction -> RespondWithTextState"
    )
    logger.debug("state=%s action=%s", _state, action)
    return RespondWithTextState(message=action.message)


def reduce_execute_tool_calls_with_append_human_tool_response_to_responses(
    state: ExecuteToolCallsState,
    action: AppendHumanToolResponseToResponsesAction,
    logger: logging.Logger,
) -> ExecuteToolCallsState:
    logger.info(
        "ExecuteToolCallsState + AppendHumanToolResponseToResponsesAction -> ExecuteToolCallsState"
    )
    logger.debug("state=%s action=%s", state, action)
    return ExecuteToolCallsState(
        pending_tool_calls=state.pending_tool_calls,
        current_tool_call=state.current_tool_call,
        human_tool_responses=state.human_tool_responses + [action.response],
    )


def reduce_execute_tool_calls_with_execute_next_tool(
    state: ExecuteToolCallsState, _action: ExecuteNextToolAction
) -> ExecuteToolCallsState:
    _action.logger.info(
        "ExecuteToolCallsState + ExecuteNextToolAction -> ExecuteToolCallsState"
    )
    _action.logger.debug("state=%s action=%s", state, _action)
    # noinspection PyTypeChecker
    return ExecuteToolCallsState(
        pending_tool_calls=state.pending_tool_calls[1:],
        current_tool_call=state.pending_tool_calls[0],
        human_tool_responses=state.human_tool_responses,
    )


async def invoke_llm_execute_next_tool_or_finish_tool_execution(
    substate: SequentialToolExecutionState | None,
    state_key: str,
    invoke_llm: Callable[[], Awaitable[dict]],
    logger: logging.Logger,
) -> dict:
    if substate is None:
        return await invoke_llm()

    if (
        isinstance(substate, ExecuteToolCallsState)
        and len(substate.pending_tool_calls) > 0
    ):
        return {
            state_key: reduce_execute_tool_calls_with_execute_next_tool(
                state=substate,
                _action=ExecuteNextToolAction(),
                logger=logger,
            )
        }

    if isinstance(substate, ExecuteToolCallsState):
        combined = "\n\n".join(substate.human_tool_responses)
        return {
            state_key: reduce_execute_tool_calls_with_finish_execute_tool_calls(
                _state=substate,
                action=FinishExecuteToolCallsAction(
                    message=AIMessage(content=combined),
                ),
                logger=logger,
            ),
        }

    raise ValueError(f"sequential_tool_execution_state: {type(substate).__name__}")


async def init_execute_tool_calls_or_respond_with_text(
    llm: LlmWithSystemPrompt,
    messages: list[BaseMessage],
    state_key: str,
    logger: logging.Logger,
    label: str,
    add_response_to_messages: bool,
) -> dict:
    logger.info("[%s] handling", label)
    response = await llm.ainvoke(messages=messages)

    if not response.tool_calls:
        logger.info("[%s] text response", label)
        return {
            state_key: reduce_none_with_respond_with_text(
                _state=None,
                action=RespondWithTextAction(
                    message=AIMessage(content=response.content),
                ),
                logger=logger,
            ),
        }

    logger.info(
        "[%s] tool_calls=%s",
        label,
        [tc["name"] for tc in response.tool_calls],
    )

    tool_calls = response.tool_calls

    # noinspection PyTypeChecker
    result = {
        state_key: reduce_none_with_init_execute_tool_calls(
            _state=None,
            action=InitExecuteToolCallsAction(
                pending_tool_calls=tool_calls[1:],
                current_tool_call=tool_calls[0],
            ),
            logger=logger,
        ),
    }

    if add_response_to_messages:
        # noinspection PyTypeChecker
        result["messages"] = [response]  # todo for sebstemmer: do this in substate

    return result


def route_by_sequential_tool_execution_state(
    substate: SequentialToolExecutionState | None,
    text_response_node_name: str,
    logger: logging.Logger,
) -> str:
    if isinstance(substate, RespondWithTextState):
        return text_response_node_name
    if isinstance(substate, ExecuteToolCallsState):
        return substate.current_tool_call["name"]

    logger.error("Unexpected substate: %s", type(substate).__name__)
    return END


SequentialToolExecutionStateType = TypeVar(
    "SequentialToolExecutionStateType", bound=SequentialToolExecutionState
)


def parse_sequential_tool_execution_state(
    sequential_tool_execution_state: SequentialToolExecutionState | None,
    expected_type: type[SequentialToolExecutionStateType],
) -> SequentialToolExecutionStateType:
    if sequential_tool_execution_state is None:
        raise ValueError(f"Expected {expected_type.__name__}, got None")
    if not isinstance(sequential_tool_execution_state, expected_type):
        raise ValueError(
            f"Expected {expected_type.__name__}, got {type(sequential_tool_execution_state).__name__}"
        )
    return sequential_tool_execution_state
