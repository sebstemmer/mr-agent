import logging

from dependency_injector import containers, providers
from utils.common.src.config import settings
from utils.common.src.llm import CHAT_GPT_5_4_MINI_MODEL
from weather.src.container import WeatherContainer

from agent_v2.agent.create_agent import CreateAgent
from agent_v2.agent.handle_incoming_message import HandleIncomingMessage
from agent_v2.agent.node.merge_readable_tool_messages_node import (
    MergeReadableToolMessagesNode,
)
from agent_v2.agent.node.planner_node import PlannerNode
from agent_v2.agent.state.create_execute_tool_call_state import (
    CreateExecuteToolCallState,
)
from agent_v2.agent.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)
from agent_v2.agent.state.dispatch_respond_with_text_action import (
    DispatchRespondWithTextAction,
)
from agent_v2.agent.tool_registry import ToolRegistryEntry
from agent_v2.email.src.container import EmailAgentContainer
from agent_v2.email.src.send_email_tool import TOOL_NAME as _SEND_EMAIL_TOOL_NAME
from agent_v2.weather.src.container import WeatherAgentContainer
from agent_v2.weather.src.get_weather_tool import TOOL_NAME as _GET_WEATHER_TOOL_NAME

SYSTEM_PROMPT = (
    "You are a personal assistant. Today is {today}. "
    "After all tools have finished, do not repeat or summarize the tool results. "
    "If there is nothing new to add, just say 'Done'."
)


class AgentV2Container(containers.DeclarativeContainer):
    weather_container: WeatherContainer = providers.DependenciesContainer()
    send_message = providers.Dependency()

    _logger = providers.Singleton(logging.getLogger, "agent_v2")

    _dispatch_executed_tool_action = providers.Singleton(
        DispatchExecutedToolAction,
        logger=_logger,
        send_message=send_message,
    )

    _dispatch_respond_with_text_action = providers.Singleton(
        DispatchRespondWithTextAction,
        logger=_logger,
        send_message=send_message,
    )

    weather_agent_container = providers.Container(
        WeatherAgentContainer,
        weather_container=weather_container,
        dispatch_executed_tool_action=_dispatch_executed_tool_action,
    )

    email_agent_container = providers.Container(
        EmailAgentContainer,
        dispatch_executed_tool_action=_dispatch_executed_tool_action,
    )

    planner_node = providers.Singleton(
        PlannerNode,
        api_key=settings.OPENAI_API_KEY,
        model=CHAT_GPT_5_4_MINI_MODEL,
        system_prompt=SYSTEM_PROMPT,
        tools=providers.List(
            weather_agent_container.get_weather_tool,
            email_agent_container.send_email_tool,
        ),
        logger=_logger,
        dispatch_respond_with_text_action=_dispatch_respond_with_text_action,
    )

    _tool_registry = providers.Dict(
        {
            _GET_WEATHER_TOOL_NAME: providers.Singleton(
                ToolRegistryEntry,
                node_name="get_weather",
                display_name="Get Weather Tool",
            ),
            _SEND_EMAIL_TOOL_NAME: providers.Singleton(
                ToolRegistryEntry,
                node_name="send_email",
                display_name="Send Email Tool",
            ),
        }
    )

    _merge_readable_tool_messages_node = providers.Singleton(
        MergeReadableToolMessagesNode,
        logger=_logger,
    )

    _create_execute_tool_call_state = providers.Singleton(
        CreateExecuteToolCallState,
        logger=_logger,
        send_message=send_message,
        tool_registry=_tool_registry,
    )

    _create_agent = providers.Singleton(
        CreateAgent,
        planner_node=planner_node,
        get_weather_node=weather_agent_container.get_weather_node,
        send_email_node=email_agent_container.send_email_node,
        merge_readable_tool_messages_node=_merge_readable_tool_messages_node,
        tool_registry=_tool_registry,
        create_execute_tool_call_state=_create_execute_tool_call_state,
        logger=_logger,
    )

    _agent = providers.Singleton(
        lambda create_agent: create_agent.create(),
        create_agent=_create_agent,
    )

    handle_incoming_message = providers.Singleton(
        HandleIncomingMessage,
        agent=_agent,
    )
