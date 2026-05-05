from logging import Logger

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Send

from agent_v2.agent.agent_state import (
    AgentState,
    ExecuteToolCallsState,
    ExecuteToolCallState,
    InitState,
)
from agent_v2.agent.planner_node import PlannerNode
from agent_v2.email.src.send_email_node import SendEmailNode
from agent_v2.email.src.send_email_tool import TOOL_NAME as _SEND_EMAIL_TOOL_NAME
from agent_v2.weather.src.get_weather_node import GetWeatherNode
from agent_v2.weather.src.get_weather_tool import TOOL_NAME as _GET_WEATHER_TOOL_NAME


class CreateAgent:
    _PLANNER_NODE_NAME = "planner"
    _GET_WEATHER_NODE_NAME = "get_weather"
    _SEND_EMAIL_NODE_NAME = "send_email"

    def __init__(
        self,
        planner_node: PlannerNode,
        get_weather_node: GetWeatherNode,
        send_email_node: SendEmailNode,
        logger: Logger,
    ):
        self._planner_node = planner_node
        self._get_weather_node = get_weather_node
        self._send_email_node = send_email_node
        self._logger = logger

    def create(self) -> CompiledStateGraph:
        # noinspection PyTypeChecker
        graph = StateGraph(AgentState)

        # noinspection PyTypeChecker
        graph.add_node(self._PLANNER_NODE_NAME, self._planner_node.plan)
        # noinspection PyTypeChecker
        graph.add_node(self._GET_WEATHER_NODE_NAME, self._get_weather_node.get)
        # noinspection PyTypeChecker
        graph.add_node(self._SEND_EMAIL_NODE_NAME, self._send_email_node.send)

        graph.add_edge(START, self._PLANNER_NODE_NAME)

        tool_nodes = [self._GET_WEATHER_NODE_NAME, self._SEND_EMAIL_NODE_NAME]

        graph.add_conditional_edges(self._PLANNER_NODE_NAME, self._route_after_planner)

        [graph.add_edge(node, self._PLANNER_NODE_NAME) for node in tool_nodes]

        return graph.compile(checkpointer=MemorySaver())

    def _route_after_planner(self, agent_state: AgentState) -> str | list[Send]:
        state = agent_state["state"]

        # todo for sebstemmer: use action
        if isinstance(state, ExecuteToolCallsState):
            return [
                Send(
                    self._map_tool_name_to_tool_node_name(call["name"]),
                    {
                        "state": ExecuteToolCallState(
                            messages=state.messages,
                            call=call,
                        )
                    },
                )
                for call in state.calls
            ]
        if isinstance(state, InitState):
            return END

        raise ValueError(f"Unexpected state: {type(state).__name__}")

    def _map_tool_name_to_tool_node_name(self, tool_name) -> str:
        node_name_to_tool_node_name = {
            _GET_WEATHER_TOOL_NAME: self._GET_WEATHER_NODE_NAME,
            _SEND_EMAIL_TOOL_NAME: self._SEND_EMAIL_NODE_NAME,
        }
        return node_name_to_tool_node_name[tool_name]
