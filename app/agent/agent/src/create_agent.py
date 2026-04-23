from logging import Logger

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent.agent.src.router_node import RouterNode
from agent.common.sequential_tool_execution_state import (
    AppendHumanToolResponseToResponsesAction,
    ExecuteToolCallsState,
    SequentialToolExecutionState,
    reduce_execute_tool_calls_with_append_human_tool_response_to_responses,
    route_by_sequential_tool_execution_state,
)
from agent.common.text_response_node import TextResponseNode
from agent.job_search.src.handle_job_search_node import HandleJobSearchNode
from agent.job_search.src.handle_job_search_tool import TOOL_NAME as _JOB_SEARCH
from agent.state.agent_state import (
    SEQUENTIAL_TOOL_EXECUTION_STATE_KEY,
    AgentState,
    get_sequential_tool_execution_state,
)
from agent.tasks.create_tasks_subgraph import CreateTasksSubgraph
from agent.tasks.personal_task_list_tool import TOOL_NAME as _TASKS
from agent.weather.src.handle_weather_node import HandleWeatherNode
from agent.weather.src.handle_weather_tool import TOOL_NAME as _WEATHER

_ROUTER = "router"
_TEXT_RESPONSE = "text_response"


class CreateAgent:
    def __init__(
        self,
        router_node: RouterNode,
        text_response_node: TextResponseNode,
        handle_weather_node: HandleWeatherNode,
        handle_job_search_node: HandleJobSearchNode,
        create_tasks_subgraph: CreateTasksSubgraph,
        logger: Logger,
    ):
        self._router_node = router_node
        self._text_response_node = text_response_node
        self._handle_weather_node = handle_weather_node
        self._handle_job_search_node = handle_job_search_node
        self._create_tasks_subgraph = create_tasks_subgraph
        self._logger = logger

    def _route_after_router(self, state: AgentState) -> str:
        return route_by_sequential_tool_execution_state(
            substate=get_sequential_tool_execution_state(
                state=state,
                expected_type=SequentialToolExecutionState,
            ),
            text_response_node_name=_TEXT_RESPONSE,
            logger=self._logger,
        )

    def _append_to_human_tool_responses(self, state: AgentState, response: str) -> dict:
        substate = get_sequential_tool_execution_state(
            state=state, expected_type=ExecuteToolCallsState
        )
        return {
            SEQUENTIAL_TOOL_EXECUTION_STATE_KEY: reduce_execute_tool_calls_with_append_human_tool_response_to_responses(
                state=substate,
                action=AppendHumanToolResponseToResponsesAction(
                    response=response,
                ),
                logger=self._logger,
            ),
        }

    def create(self) -> CompiledStateGraph:
        tasks_subgraph = self._create_tasks_subgraph.create()

        async def _weather(state: AgentState) -> dict:
            result = await self._handle_weather_node.handle(
                messages=state["messages"],
            )
            content = result["messages"][0].content
            return {
                "messages": result["messages"],
                **self._append_to_human_tool_responses(state=state, response=content),
            }

        async def _job_search(state: AgentState) -> dict:
            result = await self._handle_job_search_node.handle(
                messages=state["messages"],
            )
            content = result["messages"][0].content
            return {
                "messages": result["messages"],
                **self._append_to_human_tool_responses(state=state, response=content),
            }

        async def _tasks(state: AgentState) -> dict:
            result = await tasks_subgraph.ainvoke(state)
            last_message = result["messages"][-1]
            return {
                "messages": result["messages"],
                **self._append_to_human_tool_responses(
                    state=state, response=last_message.content
                ),
            }

        memory = MemorySaver()

        # noinspection PyTypeChecker
        graph = StateGraph(AgentState)

        # noinspection PyTypeChecker
        graph.add_node(_ROUTER, self._router_node.route)
        # noinspection PyTypeChecker
        graph.add_node(_TEXT_RESPONSE, self._text_response_node.execute)
        # noinspection PyTypeChecker
        graph.add_node(_WEATHER, _weather)
        # noinspection PyTypeChecker
        graph.add_node(_JOB_SEARCH, _job_search)
        # noinspection PyTypeChecker
        graph.add_node(_TASKS, _tasks)

        graph.add_edge(START, _ROUTER)
        graph.add_conditional_edges(_ROUTER, self._route_after_router)
        graph.add_edge(_TEXT_RESPONSE, END)

        for node in (_WEATHER, _JOB_SEARCH, _TASKS):
            graph.add_edge(node, _ROUTER)

        return graph.compile(checkpointer=memory)
