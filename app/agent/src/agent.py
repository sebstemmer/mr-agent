from typing import Annotated, TypedDict

from job_search.src.handle_job_search import JOB_SEARCH_BRANCH, HandleJobSearch
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.graph.state import CompiledStateGraph
from weather.src.handle_weather import WEATHER_BRANCH, HandleWeather

from agent.src.classify_intent import ClassifyIntent


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    current_branch: str | None


def _route_branch(state: AgentState) -> str:
    branch = state.get("current_branch")
    if branch == WEATHER_BRANCH:
        return WEATHER_BRANCH
    if branch == JOB_SEARCH_BRANCH:
        return JOB_SEARCH_BRANCH
    return "classify"


def _route_after_branch(state: AgentState) -> str:
    if state.get("current_branch") is None:
        return "classify"
    return END


def create_agent(
    classify_intent: ClassifyIntent,
    handle_weather: HandleWeather,
    handle_job_search: HandleJobSearch,
) -> CompiledStateGraph:
    classify_node = "classify"
    weather_node = WEATHER_BRANCH
    job_search_node = JOB_SEARCH_BRANCH
    end_node = END

    async def _classify(state: AgentState):
        return await classify_intent.classify(messages=state["messages"])

    async def _weather(state: AgentState):
        return await handle_weather.handle(messages=state["messages"])

    async def _job_search(state: AgentState):
        return await handle_job_search.handle(messages=state["messages"])

    memory = MemorySaver()

    # noinspection PyTypeChecker
    graph = StateGraph(AgentState)

    # noinspection PyTypeChecker
    graph.add_node(classify_node, _classify)

    # noinspection PyTypeChecker
    graph.add_node(weather_node, _weather)

    # noinspection PyTypeChecker
    graph.add_node(job_search_node, _job_search)

    graph.add_conditional_edges(
        START,
        _route_branch,
        {
            WEATHER_BRANCH: weather_node,
            JOB_SEARCH_BRANCH: job_search_node,
            "classify": classify_node,
        },
    )
    graph.add_edge(classify_node, end_node)
    graph.add_conditional_edges(
        weather_node,
        _route_after_branch,
        {"classify": classify_node, end_node: end_node},
    )
    graph.add_conditional_edges(
        job_search_node,
        _route_after_branch,
        {"classify": classify_node, end_node: end_node},
    )

    return graph.compile(checkpointer=memory)
