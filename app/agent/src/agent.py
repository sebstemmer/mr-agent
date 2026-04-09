from typing import Annotated, TypedDict

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
    if state.get("current_branch") == WEATHER_BRANCH:
        return WEATHER_BRANCH
    return "classify"


def create_agent(
    classify_intent: ClassifyIntent,
    handle_weather: HandleWeather,
) -> CompiledStateGraph:
    classify_node = "classify"
    weather_node = WEATHER_BRANCH

    async def _classify(state: AgentState):
        return await classify_intent.classify(messages=state["messages"])

    async def _weather(state: AgentState):
        return await handle_weather.handle(messages=state["messages"])

    memory = MemorySaver()

    # noinspection PyTypeChecker
    graph = StateGraph(AgentState)

    # noinspection PyTypeChecker
    graph.add_node(classify_node, _classify)

    # noinspection PyTypeChecker
    graph.add_node(weather_node, _weather)

    graph.add_conditional_edges(
        START,
        _route_branch,
        {WEATHER_BRANCH: weather_node, "classify": classify_node},
    )
    graph.add_edge(classify_node, END)
    graph.add_edge(weather_node, END)

    return graph.compile(checkpointer=memory)
