from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent.agent.src.router_node import RouterNode
from agent.job_search.src.handle_job_search_node import (
    JOB_SEARCH_BRANCH,
    HandleJobSearchNode,
)
from agent.state.agent_state import AgentState
from agent.tasks.create_tasks_subgraph import (
    PERSONAL_TASKS_LIST_BRANCH,
    CreateTasksSubgraph,
)
from agent.weather.src.handle_weather_node import WEATHER_BRANCH, HandleWeatherNode


class CreateAgent:
    _ROUTER = "router"
    _WEATHER = WEATHER_BRANCH
    _JOB_SEARCH = JOB_SEARCH_BRANCH
    _TASKS = PERSONAL_TASKS_LIST_BRANCH

    def __init__(
        self,
        router_node: RouterNode,
        handle_weather_node: HandleWeatherNode,
        handle_job_search_node: HandleJobSearchNode,
        create_tasks_subgraph: CreateTasksSubgraph,
    ):
        self._router_node = router_node
        self._handle_weather_node = handle_weather_node
        self._handle_job_search_node = handle_job_search_node
        self._create_tasks_subgraph = create_tasks_subgraph

    def create(self) -> CompiledStateGraph:
        async def _route(state: AgentState):
            return await self._router_node.route(messages=state["messages"])

        async def _weather(state: AgentState):
            return await self._handle_weather_node.handle(messages=state["messages"])

        async def _job_search(state: AgentState):
            return await self._handle_job_search_node.handle(messages=state["messages"])

        tasks_subgraph = self._create_tasks_subgraph.create()

        memory = MemorySaver()

        # noinspection PyTypeChecker
        graph = StateGraph(AgentState)

        # noinspection PyTypeChecker
        graph.add_node(CreateAgent._ROUTER, _route)
        # noinspection PyTypeChecker
        graph.add_node(CreateAgent._WEATHER, _weather)
        # noinspection PyTypeChecker
        graph.add_node(CreateAgent._JOB_SEARCH, _job_search)
        # noinspection PyTypeChecker
        graph.add_node(CreateAgent._TASKS, tasks_subgraph)

        graph.add_edge(START, CreateAgent._ROUTER)
        graph.add_edge(CreateAgent._WEATHER, END)
        graph.add_edge(CreateAgent._JOB_SEARCH, END)
        graph.add_edge(CreateAgent._TASKS, END)

        return graph.compile(checkpointer=memory)
