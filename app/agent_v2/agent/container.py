import logging

from dependency_injector import containers, providers
from utils.common.src.config import settings
from utils.common.src.llm import CHAT_GPT_5_4_MINI_MODEL
from weather.src.container import WeatherContainer

from agent_v2.agent.create_agent import CreateAgent
from agent_v2.agent.planner_node import PlannerNode
from agent_v2.email.src.container import EmailAgentContainer
from agent_v2.weather.src.container import WeatherAgentContainer


class AgentV2Container(containers.DeclarativeContainer):
    weather_container: WeatherContainer = providers.DependenciesContainer()

    weather_agent_container = providers.Container(
        WeatherAgentContainer,
        weather_container=weather_container,
    )

    email_agent_container = providers.Container(EmailAgentContainer)

    _logger = providers.Singleton(logging.getLogger, "agent_v2")

    planner_node = providers.Singleton(
        PlannerNode,
        api_key=settings.OPENAI_API_KEY,
        model=CHAT_GPT_5_4_MINI_MODEL,
        tools=providers.List(
            weather_agent_container.get_weather_tool,
            email_agent_container.send_email_tool,
        ),
        logger=_logger,
    )

    _create_agent = providers.Singleton(
        CreateAgent,
        planner_node=planner_node,
        get_weather_node=weather_agent_container.get_weather_node,
        send_email_node=email_agent_container.send_email_node,
        logger=_logger,
    )

    agent = providers.Singleton(
        lambda create_agent: create_agent.create(),
        create_agent=_create_agent,
    )
