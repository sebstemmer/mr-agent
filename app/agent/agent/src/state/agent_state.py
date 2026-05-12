import logging
from dataclasses import dataclass
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.messages.tool import ToolCall
from langgraph.graph import add_messages


@dataclass
class _Action:
    pass


@dataclass
class State:
    messages: list[BaseMessage]


@dataclass
class BaseState(State):
    pass


@dataclass
class ExecuteToolCallsState(State):
    calls: list[ToolCall]


@dataclass
class ExecuteToolCallState(State):
    call: ToolCall


@dataclass
class ExecutedToolsState(State):
    readable_tool_messages: list[AIMessage]


@dataclass
class NewMessageAction(_Action):
    message: BaseMessage


@dataclass
class ExecuteToolCallsAction(_Action):
    message: AIMessage
    calls: list[ToolCall]


@dataclass
class ExecutedToolAction(_Action):
    tool_message: ToolMessage
    readable_tool_message: AIMessage


@dataclass
class RespondWithTextAction(_Action):
    message: AIMessage


@dataclass
class MergeReadableToolMessagesAction(_Action):
    readable_tool_messages: list[AIMessage]


_logger = logging.getLogger(__name__)


def reduce(state: State, action: _Action) -> State:
    _logger.debug("state=%s action=%s", state, action)

    if isinstance(state, BaseState) and isinstance(action, NewMessageAction):
        _logger.info(f"{type(state).__name__} + {type(action).__name__} -> BaseState")
        return BaseState(
            messages=add_messages(state.messages, [action.message]),
        )

    if isinstance(state, BaseState) and isinstance(action, ExecuteToolCallsAction):
        _logger.info(
            f"{type(state).__name__} + {type(action).__name__} -> ExecuteToolCallsState"
        )
        return ExecuteToolCallsState(
            messages=add_messages(state.messages, [action.message]),
            calls=action.calls,
        )

    if isinstance(state, BaseState) and isinstance(action, RespondWithTextAction):
        _logger.info(f"{type(state).__name__} + {type(action).__name__} -> BaseState")
        return BaseState(
            messages=add_messages(state.messages, [action.message]),
        )

    if isinstance(state, ExecuteToolCallsState) and isinstance(
        action, ExecutedToolAction
    ):
        _logger.info(
            f"{type(state).__name__} + {type(action).__name__} -> ExecutedToolsState"
        )
        return ExecutedToolsState(
            messages=add_messages(state.messages, [action.tool_message]),
            readable_tool_messages=[action.readable_tool_message],
        )

    if isinstance(state, ExecutedToolsState) and isinstance(action, ExecutedToolAction):
        _logger.info(
            f"{type(state).__name__} + {type(action).__name__} -> ExecutedToolsState"
        )
        return ExecutedToolsState(
            messages=add_messages(state.messages, [action.tool_message]),
            readable_tool_messages=[
                *state.readable_tool_messages,
                action.readable_tool_message,
            ],
        )

    if isinstance(state, ExecutedToolsState) and isinstance(
        action, MergeReadableToolMessagesAction
    ):
        _logger.info(f"{type(state).__name__} + {type(action).__name__} -> BaseState")
        return BaseState(
            messages=add_messages(state.messages, action.readable_tool_messages),
        )

    raise ValueError(
        f"Unhandled state/action: {type(state).__name__} + {type(action).__name__}"
    )


class AgentState(TypedDict):
    state: Annotated[State, reduce]
