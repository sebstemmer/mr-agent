from logging import Logger

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Send

from agent.agent.src.node.merge_readable_tool_messages_node import (
    MergeReadableToolMessagesNode,
)
from agent.agent.src.node.planner_node import PlannerNode
from agent.agent.src.state.agent_state import (
    AgentState,
    BaseState,
    ExecuteToolCallsState,
)
from agent.agent.src.state.create_execute_tool_call_state import (
    CreateExecuteToolCallState,
)
from agent.agent.src.tool_registry import ToolRegistry
from agent.job_search.src.create_job_opening_node import CreateJobOpeningNode
from agent.job_search.src.create_job_opening_tool import (
    TOOL_NAME as _CREATE_JOB_OPENING_TOOL_NAME,
)
from agent.job_search.src.get_jobs_node import GetJobsNode
from agent.job_search.src.get_jobs_tool import TOOL_NAME as _GET_JOBS_TOOL_NAME
from agent.job_search.src.job_search_status_node import JobSearchStatusNode
from agent.job_search.src.job_search_status_tool import (
    TOOL_NAME as _JOB_SEARCH_STATUS_TOOL_NAME,
)
from agent.job_search.src.like_job_node import LikeJobNode
from agent.job_search.src.like_job_tool import TOOL_NAME as _LIKE_JOB_TOOL_NAME
from agent.tasks.src.create_task.create_task_node import CreateTaskNode
from agent.tasks.src.create_task.create_task_tool import (
    TOOL_NAME as _CREATE_TASK_TOOL_NAME,
)
from agent.tasks.src.delete_task.delete_task_node import DeleteTaskNode
from agent.tasks.src.delete_task.delete_task_tool import (
    TOOL_NAME as _DELETE_TASK_TOOL_NAME,
)
from agent.tasks.src.get_tasks.get_tasks_node import GetTasksNode
from agent.tasks.src.get_tasks.get_tasks_tool import (
    TOOL_NAME as _GET_TASKS_TOOL_NAME,
)
from agent.tasks.src.update_task.update_task_node import UpdateTaskNode
from agent.tasks.src.update_task.update_task_tool import (
    TOOL_NAME as _UPDATE_TASK_TOOL_NAME,
)
from agent.weather.src.get_weather_node import GetWeatherNode
from agent.weather.src.get_weather_tool import TOOL_NAME as _GET_WEATHER_TOOL_NAME


class CreateAgent:
    _PLANNER_NODE_NAME = "planner"
    _MERGE_READABLE_TOOL_MESSAGES_NODE_NAME = "merge_readable_tool_messages"

    def __init__(
        self,
        planner_node: PlannerNode,
        get_weather_node: GetWeatherNode,
        get_tasks_node: GetTasksNode,
        create_task_node: CreateTaskNode,
        delete_task_node: DeleteTaskNode,
        update_task_node: UpdateTaskNode,
        get_jobs_node: GetJobsNode,
        like_job_node: LikeJobNode,
        job_search_status_node: JobSearchStatusNode,
        create_job_opening_node: CreateJobOpeningNode,
        merge_readable_tool_messages_node: MergeReadableToolMessagesNode,
        tool_registry: ToolRegistry,
        create_execute_tool_call_state: CreateExecuteToolCallState,
        logger: Logger,
    ):
        self._planner_node = planner_node
        self._get_weather_node = get_weather_node
        self._get_tasks_node = get_tasks_node
        self._create_task_node = create_task_node
        self._delete_task_node = delete_task_node
        self._update_task_node = update_task_node
        self._get_jobs_node = get_jobs_node
        self._like_job_node = like_job_node
        self._job_search_status_node = job_search_status_node
        self._create_job_opening_node = create_job_opening_node
        self._merge_readable_tool_messages_node = merge_readable_tool_messages_node
        self._tool_registry = tool_registry
        self._create_execute_tool_call_state = create_execute_tool_call_state
        self._logger = logger

    def create(self) -> CompiledStateGraph:
        # noinspection PyTypeChecker
        graph = StateGraph(AgentState)

        # noinspection PyTypeChecker
        graph.add_node(self._PLANNER_NODE_NAME, self._planner_node.plan)
        # noinspection PyTypeChecker
        graph.add_node(
            self._tool_registry[_GET_WEATHER_TOOL_NAME].node_name,
            self._get_weather_node.get,
        )
        # noinspection PyTypeChecker
        graph.add_node(
            self._tool_registry[_GET_TASKS_TOOL_NAME].node_name,
            self._get_tasks_node.get,
        )
        # noinspection PyTypeChecker
        graph.add_node(
            self._tool_registry[_CREATE_TASK_TOOL_NAME].node_name,
            self._create_task_node.create,
        )
        # noinspection PyTypeChecker
        graph.add_node(
            self._tool_registry[_DELETE_TASK_TOOL_NAME].node_name,
            self._delete_task_node.delete,
        )
        # noinspection PyTypeChecker
        graph.add_node(
            self._tool_registry[_UPDATE_TASK_TOOL_NAME].node_name,
            self._update_task_node.update,
        )
        # noinspection PyTypeChecker
        graph.add_node(
            self._tool_registry[_GET_JOBS_TOOL_NAME].node_name,
            self._get_jobs_node.get,
        )
        # noinspection PyTypeChecker
        graph.add_node(
            self._tool_registry[_LIKE_JOB_TOOL_NAME].node_name,
            self._like_job_node.like,
        )
        # noinspection PyTypeChecker
        graph.add_node(
            self._tool_registry[_JOB_SEARCH_STATUS_TOOL_NAME].node_name,
            self._job_search_status_node.get,
        )
        # noinspection PyTypeChecker
        graph.add_node(
            self._tool_registry[_CREATE_JOB_OPENING_TOOL_NAME].node_name,
            self._create_job_opening_node.create,
        )
        # noinspection PyTypeChecker
        graph.add_node(
            self._MERGE_READABLE_TOOL_MESSAGES_NODE_NAME,
            self._merge_readable_tool_messages_node.merge,
        )

        graph.add_edge(START, self._PLANNER_NODE_NAME)

        graph.add_conditional_edges(self._PLANNER_NODE_NAME, self._route_after_planner)

        for entry in self._tool_registry.values():
            graph.add_edge(
                entry.node_name, self._MERGE_READABLE_TOOL_MESSAGES_NODE_NAME
            )

        graph.add_edge(
            self._MERGE_READABLE_TOOL_MESSAGES_NODE_NAME, self._PLANNER_NODE_NAME
        )

        return graph.compile(checkpointer=MemorySaver())

    async def _route_after_planner(self, agent_state: AgentState) -> str | list[Send]:
        state = agent_state["state"]

        if isinstance(state, ExecuteToolCallsState):
            return [
                Send(
                    self._tool_registry[call["name"]].node_name,
                    {
                        "state": await self._create_execute_tool_call_state.create(
                            call=call,
                        )
                    },
                )
                for call in state.calls
            ]
        if isinstance(state, BaseState):
            return END

        raise ValueError(f"Unexpected state: {type(state).__name__}")
