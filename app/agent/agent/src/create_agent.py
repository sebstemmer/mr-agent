from logging import Logger

from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent.agent.src.orchestrator_node import OrchestratorNode

# from agent.agent.src.router_node import RouterNode
from agent.common.sequential_tool_execution_state import (
    AppendHumanToolResponseToResponsesAction,
    ExecuteToolCallsState,
    reduce_execute_tool_calls_with_append_human_tool_response_to_responses,
)
from agent.common.text_response_node import TextResponseNode
from agent.job_search.src.handle_job_search_node import HandleJobSearchNode
from agent.state.agent_state import (
    SEQUENTIAL_TOOL_EXECUTION_STATE_KEY,
    AgentState,
    ExecuteBranchesState,
    TextResponseState,
    get_sequential_tool_execution_state,
)
from agent.tasks.create_tasks_subgraph import CreateTasksSubgraph
from agent.weather.src.handle_weather_node import (
    HANDLE_WEATHER_NODE_NAME,
    HandleWeatherNode,
)

# _ROUTER = "router"


class CreateAgent:
    _TEXT_RESPONSE = "text_response"

    def __init__(
        self,
        orchestrator_node: OrchestratorNode,
        # router_node: RouterNode,
        text_response_node: TextResponseNode,
        handle_weather_node: HandleWeatherNode,
        handle_job_search_node: HandleJobSearchNode,
        create_tasks_subgraph: CreateTasksSubgraph,
        logger: Logger,
    ):
        self._orchestrator_node = orchestrator_node
        # self._router_node = router_node
        self._text_response_node = text_response_node
        self._handle_weather_node = handle_weather_node
        self._handle_job_search_node = handle_job_search_node
        self._create_tasks_subgraph = create_tasks_subgraph
        self._logger = logger

    @staticmethod
    def _route_after_orchestrator(state: AgentState) -> list[Send] | str:
        orchestrator_decision_state = state["orchestrator_decision_state"]

        if isinstance(orchestrator_decision_state, TextResponseState):
            return CreateAgent._TEXT_RESPONSE

        if isinstance(orchestrator_decision_state, ExecuteBranchesState):
            return [
                Send(branch.value, {"messages": state["messages"]})
                for branch in orchestrator_decision_state.branches
            ]

        raise ValueError(
            f"Unhandled orchestrator_decision_state: {type(orchestrator_decision_state).__name__}"
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
        # tasks_subgraph = self._create_tasks_subgraph.create()

        async def _weather(state: AgentState) -> dict:
            result = await self._handle_weather_node.handle(
                messages=state["messages"],
            )
            content = result["messages"][0].content
            return {
                "messages": result["messages"],
                **self._append_to_human_tool_responses(state=state, response=content),
            }

        # async def _job_search(state: AgentState) -> dict:
        #     result = await self._handle_job_search_node.handle(
        #         messages=state["messages"],
        #     )
        #     content = result["messages"][0].content
        #     return {
        #         "messages": result["messages"],
        #         **self._append_to_human_tool_responses(state=state, response=content),
        #     }

        # async def _tasks(state: AgentState) -> dict:
        #     result = await tasks_subgraph.ainvoke(state)
        #     last_message = result["messages"][-1]
        #     return {
        #         "messages": result["messages"],
        #         **self._append_to_human_tool_responses(
        #             state=state, response=last_message.content
        #         ),
        #     }

        orchestrator = "orchestrator"
        memory = MemorySaver()

        # noinspection PyTypeChecker
        graph = StateGraph(AgentState)

        # noinspection PyTypeChecker
        graph.add_node(orchestrator, self._orchestrator_node.orchestrate)
        # noinspection PyTypeChecker
        graph.add_node(CreateAgent._TEXT_RESPONSE, self._text_response_node.execute)
        # noinspection PyTypeChecker
        graph.add_node(HANDLE_WEATHER_NODE_NAME, _weather)
        # graph.add_node(_JOB_SEARCH, _job_search)
        # graph.add_node(_TASKS, _tasks)

        graph.add_edge(START, orchestrator)
        graph.add_conditional_edges(orchestrator, self._route_after_orchestrator)
        graph.add_edge(CreateAgent._TEXT_RESPONSE, END)

        graph.add_edge(HANDLE_WEATHER_NODE_NAME, END)
        # for node in (_JOB_SEARCH, _TASKS):
        #     graph.add_edge(node, _ROUTER)

        return graph.compile(checkpointer=memory)
