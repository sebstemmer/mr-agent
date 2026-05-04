from logging import Logger

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, Send, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent_v2.agent.agent_state import (
    AgentState,
    ExecuteToolAction,
    ExecuteToolCallsState,
)
from agent_v2.agent.planner_node import PlannerNode
from agent_v2.weather.src.get_weather_node import GetWeatherNode
from agent_v2.weather.src.get_weather_tool import GetWeatherTool


class CreateAgent:
    _PLANNER_NODE_NAME = "planner"
    _GET_WEATHER_NODE_NAME = "get_weather"

    def __init__(
        self,
        planner_node: PlannerNode,
        get_weather_node: GetWeatherNode,
        logger: Logger,
    ):
        self._planner_node = planner_node
        self._get_weather_node = get_weather_node
        self._logger = logger

    def create(self) -> CompiledStateGraph:
        graph = StateGraph(AgentState)

        graph.add_node(self._PLANNER_NODE_NAME, self._planner_node)
        graph.add_node(self._GET_WEATHER_NODE_NAME, self._get_weather_node)

        graph.add_edge(START, self._PLANNER_NODE_NAME)

        tool_nodes = [self._GET_WEATHER_NODE_NAME]

        graph.add_conditional_edges(self._PLANNER_NODE_NAME, self._route_after_planner)

        [graph.add_edge(node, self._PLANNER_NODE_NAME) for node in tool_nodes]

        return graph.compile(checkpointer=MemorySaver())

    def _route_after_planner(self, agent_state: AgentState) -> str | list[Send]:
        tool_calls_state = agent_state["tool_calls_state"]

        if isinstance(tool_calls_state, ExecuteToolCallsState):
            return [
                Send(
                    self._map_tool_name_to_tool_node_name(call["name"]),
                    {
                        "messages": agent_state["messages"],
                        "tool_state": ExecuteToolAction(logger=self._logger, call=call),
                    },
                )
                for call in tool_calls_state.calls
            ]
        else:
            pass

    def _map_tool_name_to_tool_node_name(self, tool_name) -> str:
        node_name_to_tool_node_name = {
            GetWeatherTool.name: self._GET_WEATHER_NODE_NAME,
        }
        return node_name_to_tool_node_name[tool_name]
