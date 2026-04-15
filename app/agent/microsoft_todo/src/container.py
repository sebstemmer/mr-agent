import logging

from dependency_injector import containers, providers
from microsoft_todo.src.container import MicrosoftTodoContainer
from utils.common.src.config import settings
from utils.common.src.llm import CHAT_GPT_5_4_MINI_MODEL

from agent.microsoft_todo.src.create_task_tool import CreateTaskTool
from agent.microsoft_todo.src.get_tasks_tool import GetTasksTool
from agent.microsoft_todo.src.handle_todo_node import HandleTodoNode
from agent.microsoft_todo.src.handle_todo_tool import HandleTodoTool


class TodoAgentContainer(containers.DeclarativeContainer):
    microsoft_todo_container: MicrosoftTodoContainer = providers.DependenciesContainer()

    system_prompt = providers.Dependency(instance_of=str)

    create_task_tool = providers.Singleton(
        CreateTaskTool,
        todo_client=microsoft_todo_container.microsoft_todo_client,
    )
    get_tasks_tool = providers.Singleton(
        GetTasksTool,
        todo_client=microsoft_todo_container.microsoft_todo_client,
    )
    handle_todo_tool = providers.Singleton(HandleTodoTool)
    handle_todo_node = providers.Singleton(
        HandleTodoNode,
        api_key=settings.OPENAI_API_KEY,
        model=CHAT_GPT_5_4_MINI_MODEL,
        system_prompt=system_prompt,
        create_task_tool=create_task_tool,
        get_tasks_tool=get_tasks_tool,
        logger=providers.Singleton(logging.getLogger, "todo"),
    )
