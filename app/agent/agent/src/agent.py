from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.graph.state import CompiledStateGraph

from agent.agent.src.classify_intent_node import ClassifyIntentNode
from agent.job_search.src.handle_job_search_node import (
    JOB_SEARCH_BRANCH,
    HandleJobSearchNode,
)
from agent.microsoft_todo.src.handle_todo_node import TODO_BRANCH, HandleTodoNode
from agent.weather.src.handle_weather_node import WEATHER_BRANCH, HandleWeatherNode

_CLASSIFY_NODE = "classify"
_WEATHER_NODE = WEATHER_BRANCH
_JOB_SEARCH_NODE = JOB_SEARCH_BRANCH
_TODO_NODE = TODO_BRANCH


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    current_branch: str | None


def _route_from_start(state: AgentState) -> str:
    branch = state.get("current_branch")
    if branch == WEATHER_BRANCH:
        return _WEATHER_NODE
    if branch == JOB_SEARCH_BRANCH:
        return _JOB_SEARCH_NODE
    if branch == TODO_BRANCH:
        return _TODO_NODE
    return _CLASSIFY_NODE


def _route_after_classify(state: AgentState) -> str:
    branch = state.get("current_branch")
    if branch == WEATHER_BRANCH:
        return _WEATHER_NODE
    if branch == JOB_SEARCH_BRANCH:
        return _JOB_SEARCH_NODE
    if branch == TODO_BRANCH:
        return _TODO_NODE
    return END


def _route_after_branch(state: AgentState) -> str:
    if state.get("current_branch") is None:
        return _CLASSIFY_NODE
    return END


def create_agent(
    classify_intent_node: ClassifyIntentNode,
    handle_weather_node: HandleWeatherNode,
    handle_job_search_node: HandleJobSearchNode,
    handle_todo_node: HandleTodoNode,
) -> CompiledStateGraph:
    async def _classify(state: AgentState):
        return await classify_intent_node.classify(messages=state["messages"])

    async def _weather(state: AgentState):
        return await handle_weather_node.handle(messages=state["messages"])

    async def _job_search(state: AgentState):
        return await handle_job_search_node.handle(messages=state["messages"])

    async def _todo(state: AgentState):
        return await handle_todo_node.handle(messages=state["messages"])

    memory = MemorySaver()

    # noinspection PyTypeChecker
    graph = StateGraph(AgentState)

    # noinspection PyTypeChecker
    graph.add_node(_CLASSIFY_NODE, _classify)
    # noinspection PyTypeChecker
    graph.add_node(_WEATHER_NODE, _weather)
    # noinspection PyTypeChecker
    graph.add_node(_JOB_SEARCH_NODE, _job_search)
    # noinspection PyTypeChecker
    graph.add_node(_TODO_NODE, _todo)

    graph.add_conditional_edges(
        START,
        _route_from_start,
        {
            _WEATHER_NODE: _WEATHER_NODE,
            _JOB_SEARCH_NODE: _JOB_SEARCH_NODE,
            _TODO_NODE: _TODO_NODE,
            _CLASSIFY_NODE: _CLASSIFY_NODE,
        },
    )
    graph.add_conditional_edges(
        _CLASSIFY_NODE,
        _route_after_classify,
        {
            _WEATHER_NODE: _WEATHER_NODE,
            _JOB_SEARCH_NODE: _JOB_SEARCH_NODE,
            _TODO_NODE: _TODO_NODE,
            END: END,
        },
    )
    graph.add_conditional_edges(
        _WEATHER_NODE,
        _route_after_branch,
        {_CLASSIFY_NODE: _CLASSIFY_NODE, END: END},
    )
    graph.add_conditional_edges(
        _JOB_SEARCH_NODE,
        _route_after_branch,
        {_CLASSIFY_NODE: _CLASSIFY_NODE, END: END},
    )
    graph.add_conditional_edges(
        _TODO_NODE,
        _route_after_branch,
        {_CLASSIFY_NODE: _CLASSIFY_NODE, END: END},
    )

    return graph.compile(checkpointer=memory)
