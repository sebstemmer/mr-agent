import logging

from dependency_injector import containers, providers
from microsoft_todo.src.container import MicrosoftTodoContainer
from utils.common.src.config import settings
from utils.common.src.llm import CHAT_GPT_5_4_MINI_MODEL

from agent.common.text_response_node import TextResponseNode
from agent.tasks.complete_task.complete_task_node import CompleteTaskNode
from agent.tasks.complete_task.complete_task_tool import CompleteTaskTool
from agent.tasks.create_task.create_task_node import CreateTaskNode
from agent.tasks.create_task.create_task_tool import CreateTaskTool
from agent.tasks.create_tasks_subgraph import (
    PERSONAL_TASK_LIST_BRANCH,
    CreateTasksSubgraph,
)
from agent.tasks.delete_task.delete_task_node import DeleteTaskNode
from agent.tasks.delete_task.delete_task_tool import DeleteTaskTool
from agent.tasks.get_tasks.get_tasks_node import GetTasksNode
from agent.tasks.get_tasks.get_tasks_tool import GetTasksTool
from agent.tasks.personal_task_list_tool import PersonalTaskListTool
from agent.tasks.tasks_router_node import TasksRouterNode
from agent.tasks.tasks_state import TASKS_SEQUENTIAL_TOOL_EXECUTION_STATE_KEY
from agent.tasks.update_task.update_task_node import UpdateTaskNode
from agent.tasks.update_task.update_task_tool import UpdateTaskTool


class TasksSubgraphContainer(containers.DeclarativeContainer):
    microsoft_todo_container: MicrosoftTodoContainer = providers.DependenciesContainer()

    system_prompt = providers.Dependency(instance_of=str)

    # Tools
    create_task_tool = providers.Singleton(
        CreateTaskTool,
        todo_client=microsoft_todo_container.microsoft_todo_client,
    )
    get_tasks_tool = providers.Singleton(
        GetTasksTool,
        todo_client=microsoft_todo_container.microsoft_todo_client,
    )
    update_task_tool = providers.Singleton(
        UpdateTaskTool,
        todo_client=microsoft_todo_container.microsoft_todo_client,
    )
    complete_task_tool = providers.Singleton(
        CompleteTaskTool,
        todo_client=microsoft_todo_container.microsoft_todo_client,
    )
    delete_task_tool = providers.Singleton(
        DeleteTaskTool,
        todo_client=microsoft_todo_container.microsoft_todo_client,
    )
    personal_task_list_tool = providers.Singleton(PersonalTaskListTool)

    # Logger
    _logger = providers.Singleton(logging.getLogger, "tasks")

    # Nodes
    router_node = providers.Singleton(
        TasksRouterNode,
        api_key=settings.OPENAI_API_KEY,
        model=CHAT_GPT_5_4_MINI_MODEL,
        system_prompt=system_prompt,
        tools=providers.List(
            create_task_tool,
            get_tasks_tool,
            update_task_tool,
            complete_task_tool,
            delete_task_tool,
        ),
        branch_name=PERSONAL_TASK_LIST_BRANCH,
        logger=_logger,
    )
    text_response_node = providers.Singleton(
        TextResponseNode,
        state_key=TASKS_SEQUENTIAL_TOOL_EXECUTION_STATE_KEY,
        logger=_logger,
    )
    create_task_node = providers.Singleton(
        CreateTaskNode,
        create_task_tool=create_task_tool,
        logger=_logger,
    )
    get_tasks_node = providers.Singleton(
        GetTasksNode,
        get_tasks_tool=get_tasks_tool,
        logger=_logger,
    )
    complete_task_node = providers.Singleton(
        CompleteTaskNode,
        complete_task_tool=complete_task_tool,
        logger=_logger,
    )
    delete_task_node = providers.Singleton(
        DeleteTaskNode,
        delete_task_tool=delete_task_tool,
        logger=_logger,
    )
    update_task_node = providers.Singleton(
        UpdateTaskNode,
        update_task_tool=update_task_tool,
        logger=_logger,
    )

    # Subgraph
    create_tasks_subgraph = providers.Singleton(
        CreateTasksSubgraph,
        router_node=router_node,
        text_response_node=text_response_node,
        create_task_node=create_task_node,
        get_tasks_node=get_tasks_node,
        complete_task_node=complete_task_node,
        delete_task_node=delete_task_node,
        update_task_node=update_task_node,
        logger=_logger,
    )
