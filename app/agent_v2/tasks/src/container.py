import logging

from dependency_injector import containers, providers
from microsoft_todo.src.container import MicrosoftTodoContainer
from utils.common.src.config import settings

from agent_v2.tasks.src.create_task.create_task_node import CreateTaskNode
from agent_v2.tasks.src.create_task.create_task_tool import CreateTaskTool
from agent_v2.tasks.src.delete_task.delete_task_node import DeleteTaskNode
from agent_v2.tasks.src.delete_task.delete_task_tool import DeleteTaskTool
from agent_v2.tasks.src.get_tasks.get_tasks_node import GetTasksNode
from agent_v2.tasks.src.get_tasks.get_tasks_tool import GetTasksTool
from agent_v2.tasks.src.task_lists import PERSONAL_TASKS


class TasksAgentContainer(containers.DeclarativeContainer):
    microsoft_todo_container: MicrosoftTodoContainer = providers.DependenciesContainer()
    dispatch_executed_tool_action = providers.Dependency()

    _logger = providers.Singleton(logging.getLogger, "agent_v2.tasks")

    _list_name_to_id = providers.Dict(
        {
            PERSONAL_TASKS.name: settings.MICROSOFT_TODO_LIST_ID,
        }
    )

    get_tasks_tool = providers.Singleton(
        GetTasksTool,
        todo_client=microsoft_todo_container.microsoft_todo_client,
        list_name_to_id=_list_name_to_id,
    )

    get_tasks_node = providers.Singleton(
        GetTasksNode,
        get_tasks_tool=get_tasks_tool,
        dispatch_executed_tool_action=dispatch_executed_tool_action,
        logger=_logger,
    )

    create_task_tool = providers.Singleton(
        CreateTaskTool,
        todo_client=microsoft_todo_container.microsoft_todo_client,
        list_name_to_id=_list_name_to_id,
    )

    create_task_node = providers.Singleton(
        CreateTaskNode,
        create_task_tool=create_task_tool,
        dispatch_executed_tool_action=dispatch_executed_tool_action,
        logger=_logger,
    )

    delete_task_tool = providers.Singleton(
        DeleteTaskTool,
        todo_client=microsoft_todo_container.microsoft_todo_client,
        list_name_to_id=_list_name_to_id,
    )

    delete_task_node = providers.Singleton(
        DeleteTaskNode,
        delete_task_tool=delete_task_tool,
        dispatch_executed_tool_action=dispatch_executed_tool_action,
        logger=_logger,
    )
