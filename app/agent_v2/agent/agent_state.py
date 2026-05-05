import logging
from dataclasses import dataclass
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.messages.tool import ToolCall, ToolMessage
from langgraph.graph import add_messages


@dataclass
class State:
    messages: list[BaseMessage]


@dataclass
class InitState(State):
    pass


@dataclass
class ExecuteToolCallsState(State):
    calls: list[ToolCall]
    displayable_messages: list[str]


@dataclass
class ExecuteToolCallState(State):
    call: ToolCall


@dataclass
class ExecutedToolsState(State):
    displayable_messages: list[str]


@dataclass
class _Action:
    pass


@dataclass
class NewMessageAction(_Action):
    message: BaseMessage


@dataclass
class ExecuteToolCallsAction(_Action):
    message: AIMessage
    calls: list[ToolCall]


@dataclass
class ExecutedToolAction(_Action):
    message: ToolMessage
    displayable_message: str


@dataclass
class RespondWithTextAction(_Action):
    message: AIMessage


_logger = logging.getLogger(__name__)


def reduce(state: State, action: _Action) -> State:
    _logger.debug("state=%s action=%s", state, action)

    if isinstance(state, InitState) and isinstance(action, NewMessageAction):
        _logger.info(
            f"{type(state).__name__} + {type(action).__name__} -> InitState"
        )
        return InitState(
            messages=add_messages(state.messages, [action.message]),
        )

    if isinstance(state, InitState) and isinstance(action, ExecuteToolCallsAction):
        _logger.info(
            f"{type(state).__name__} + {type(action).__name__} -> ExecuteToolCallsState"
        )
        return ExecuteToolCallsState(
            messages=add_messages(state.messages, [action.message]),
            calls=action.calls,
            displayable_messages=[],
        )

    if isinstance(state, InitState) and isinstance(action, RespondWithTextAction):
        _logger.info(f"{type(state).__name__} + {type(action).__name__} -> InitState")
        return InitState(
            messages=add_messages(state.messages, [action.message]),
        )

    if isinstance(state, ExecuteToolCallsState) and isinstance(
        action, ExecutedToolAction
    ):
        _logger.info(
            f"{type(state).__name__} + {type(action).__name__} -> ExecutedToolsState"
        )
        return ExecutedToolsState(
            messages=add_messages(state.messages, [action.message]),
            displayable_messages=[
                *state.displayable_messages,
                action.displayable_message,
            ],
        )

    if isinstance(state, ExecutedToolsState) and isinstance(action, ExecutedToolAction):
        _logger.info(
            f"{type(state).__name__} + {type(action).__name__} -> ExecutedToolsState"
        )
        return ExecutedToolsState(
            messages=add_messages(state.messages, [action.message]),
            displayable_messages=[
                *state.displayable_messages,
                action.displayable_message,
            ],
        )

    if isinstance(state, ExecutedToolsState) and isinstance(
        action, ExecuteToolCallsAction
    ):
        _logger.info(
            f"{type(state).__name__} + {type(action).__name__} -> ExecuteToolCallsState"
        )
        return ExecuteToolCallsState(
            messages=add_messages(state.messages, [action.message]),
            calls=action.calls,
            displayable_messages=[*state.displayable_messages],
        )

    if isinstance(state, ExecutedToolsState) and isinstance(
        action, RespondWithTextAction
    ):
        _logger.info(f"{type(state).__name__} + {type(action).__name__} -> InitState")
        return InitState(
            messages=add_messages(
                state.messages,
                [AIMessage(content="\n\n".join(state.displayable_messages))],
            ),
        )

    raise ValueError(
        f"Unhandled state/action: {type(state).__name__} + {type(action).__name__}"
    )


class AgentState(TypedDict):
    state: Annotated[State, reduce]
