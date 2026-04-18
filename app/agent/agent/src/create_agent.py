from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent.agent.src.classify_intent_node import ClassifyIntentNode
from agent.job_search.src.handle_job_search_node import (
    JOB_SEARCH_BRANCH,
    HandleJobSearchNode,
)
from agent.state.agent_state import AgentState
from agent.tasks.create_tasks_subgraph import TASKS_BRANCH, CreateTasksSubgraph
from agent.weather.src.handle_weather_node import WEATHER_BRANCH, HandleWeatherNode


class CreateAgent:
    _CLASSIFY = "classify"
    _WEATHER = WEATHER_BRANCH
    _JOB_SEARCH = JOB_SEARCH_BRANCH
    _TASKS = TASKS_BRANCH

    def __init__(
        self,
        classify_intent_node: ClassifyIntentNode,
        handle_weather_node: HandleWeatherNode,
        handle_job_search_node: HandleJobSearchNode,
        create_tasks_subgraph: CreateTasksSubgraph,
    ):
        self._classify_intent_node = classify_intent_node
        self._handle_weather_node = handle_weather_node
        self._handle_job_search_node = handle_job_search_node
        self._create_tasks_subgraph = create_tasks_subgraph

    def create(self) -> CompiledStateGraph:
        async def _classify(state: AgentState):
            return await self._classify_intent_node.classify(messages=state["messages"])

        async def _weather(state: AgentState):
            return await self._handle_weather_node.handle(messages=state["messages"])

        async def _job_search(state: AgentState):
            return await self._handle_job_search_node.handle(messages=state["messages"])

        tasks_subgraph = self._create_tasks_subgraph.create()

        memory = MemorySaver()

        # noinspection PyTypeChecker
        graph = StateGraph(AgentState)

        # noinspection PyTypeChecker
        graph.add_node(CreateAgent._CLASSIFY, _classify)
        # noinspection PyTypeChecker
        graph.add_node(CreateAgent._WEATHER, _weather)
        # noinspection PyTypeChecker
        graph.add_node(CreateAgent._JOB_SEARCH, _job_search)
        # noinspection PyTypeChecker
        graph.add_node(CreateAgent._TASKS, tasks_subgraph)

        graph.add_conditional_edges(
            START,
            self._route_from_start,
            {
                CreateAgent._WEATHER: CreateAgent._WEATHER,
                CreateAgent._JOB_SEARCH: CreateAgent._JOB_SEARCH,
                CreateAgent._TASKS: CreateAgent._TASKS,
                CreateAgent._CLASSIFY: CreateAgent._CLASSIFY,
            },
        )
        graph.add_conditional_edges(
            CreateAgent._CLASSIFY,
            self._route_after_classify,
            {
                CreateAgent._WEATHER: CreateAgent._WEATHER,
                CreateAgent._JOB_SEARCH: CreateAgent._JOB_SEARCH,
                CreateAgent._TASKS: CreateAgent._TASKS,
                END: END,
            },
        )
        graph.add_conditional_edges(
            CreateAgent._WEATHER,
            self._route_after_branch,
            {CreateAgent._CLASSIFY: CreateAgent._CLASSIFY, END: END},
        )
        graph.add_conditional_edges(
            CreateAgent._JOB_SEARCH,
            self._route_after_branch,
            {CreateAgent._CLASSIFY: CreateAgent._CLASSIFY, END: END},
        )
        graph.add_conditional_edges(
            CreateAgent._TASKS,
            self._route_after_branch,
            {CreateAgent._CLASSIFY: CreateAgent._CLASSIFY, END: END},
        )

        return graph.compile(checkpointer=memory)

    @staticmethod
    def _route_from_start(state: AgentState) -> str:
        branch = state.get("current_branch")
        if branch == WEATHER_BRANCH:
            return CreateAgent._WEATHER
        if branch == JOB_SEARCH_BRANCH:
            return CreateAgent._JOB_SEARCH
        if branch == TASKS_BRANCH:
            return CreateAgent._TASKS
        return CreateAgent._CLASSIFY

    @staticmethod
    def _route_after_classify(state: AgentState) -> str:
        branch = state.get("current_branch")
        if branch == WEATHER_BRANCH:
            return CreateAgent._WEATHER
        if branch == JOB_SEARCH_BRANCH:
            return CreateAgent._JOB_SEARCH
        if branch == TASKS_BRANCH:
            return CreateAgent._TASKS
        return END

    @staticmethod
    def _route_after_branch(state: AgentState) -> str:
        if state.get("current_branch") is None:
            return CreateAgent._CLASSIFY
        return END
