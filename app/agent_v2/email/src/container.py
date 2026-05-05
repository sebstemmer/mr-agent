import logging

from dependency_injector import containers, providers

from agent_v2.email.src.send_email_node import SendEmailNode
from agent_v2.email.src.send_email_tool import SendEmailTool


class EmailAgentContainer(containers.DeclarativeContainer):
    send_email_tool = providers.Singleton(SendEmailTool)

    send_email_node = providers.Singleton(
        SendEmailNode,
        send_email_tool=send_email_tool,
        logger=providers.Singleton(logging.getLogger, "agent_v2.email"),
    )
