from logging import Logger

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent.common.sequential_tool_execution_state import (
    SequentialToolExecutionState,
    route_by_sequential_tool_execution_state,
)
from agent.common.text_response_node import TextResponseNode
from agent.tasks.complete_task.complete_task_node import CompleteTaskNode
from agent.tasks.complete_task.complete_task_tool import _TOOL_NAME as _COMPLETE_TASK
from agent.tasks.create_task.create_task_node import CreateTaskNode
from agent.tasks.create_task.create_task_tool import _TOOL_NAME as _CREATE_TASK
from agent.tasks.delete_task.delete_task_node import DeleteTaskNode
from agent.tasks.delete_task.delete_task_tool import _TOOL_NAME as _DELETE_TASK
from agent.tasks.get_tasks.get_tasks_node import GetTasksNode
from agent.tasks.get_tasks.get_tasks_tool import _TOOL_NAME as _GET_TASKS
from agent.tasks.tasks_router_node import TasksRouterNode
from agent.tasks.tasks_state import (
    TasksState,
    get_tasks_sequential_tool_execution_state,
)
from agent.tasks.update_task.update_task_node import UpdateTaskNode
from agent.tasks.update_task.update_task_tool import _TOOL_NAME as _UPDATE_TASK

PERSONAL_TASK_LIST_BRANCH = "tasks"

_ROUTER = "router"
_TEXT_RESPONSE = "text_response"


class CreateTasksSubgraph:
    def __init__(
        self,
        router_node: TasksRouterNode,
        text_response_node: TextResponseNode,
        create_task_node: CreateTaskNode,
        get_tasks_node: GetTasksNode,
        complete_task_node: CompleteTaskNode,
        delete_task_node: DeleteTaskNode,
        update_task_node: UpdateTaskNode,
        logger: Logger,
    ):
        self._logger = logger
        self._router_node = router_node
        self._text_response_node = text_response_node
        self._create_task_node = create_task_node
        self._get_tasks_node = get_tasks_node
        self._complete_task_node = complete_task_node
        self._delete_task_node = delete_task_node
        self._update_task_node = update_task_node

    def _route_after_router(self, state: TasksState) -> str:
        return route_by_sequential_tool_execution_state(
            substate=get_tasks_sequential_tool_execution_state(
                tasks_state=state,
                expected_type=SequentialToolExecutionState,
            ),
            text_response_node_name=_TEXT_RESPONSE,
            logger=self._logger,
        )

    def create(self) -> CompiledStateGraph:
        # noinspection PyTypeChecker
        graph = StateGraph(TasksState)

        # noinspection PyTypeChecker
        graph.add_node(_ROUTER, self._router_node.route)
        # noinspection PyTypeChecker
        graph.add_node(_TEXT_RESPONSE, self._text_response_node.execute)
        # noinspection PyTypeChecker
        graph.add_node(_CREATE_TASK, self._create_task_node.execute)
        # noinspection PyTypeChecker
        graph.add_node(_GET_TASKS, self._get_tasks_node.execute)
        # noinspection PyTypeChecker
        graph.add_node(_COMPLETE_TASK, self._complete_task_node.execute)
        # noinspection PyTypeChecker
        graph.add_node(_DELETE_TASK, self._delete_task_node.execute)
        # noinspection PyTypeChecker
        graph.add_node(_UPDATE_TASK, self._update_task_node.execute)

        graph.set_entry_point(_ROUTER)

        graph.add_conditional_edges(_ROUTER, self._route_after_router)

        graph.add_edge(_TEXT_RESPONSE, END)

        for node in (
            _CREATE_TASK,
            _GET_TASKS,
            _COMPLETE_TASK,
            _DELETE_TASK,
            _UPDATE_TASK,
        ):
            graph.add_edge(node, _ROUTER)

        return graph.compile()
