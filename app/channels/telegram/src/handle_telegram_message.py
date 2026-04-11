from channels.common.src.save_or_update_chat_id_to_channel_type import (
    SaveOrUpdateChatIdToChannelType,
)
from channels.common.src.split_message import split_message
from channels.telegram.src.const import CHANNEL_TYPE
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from telegram import Update


class HandleTelegramMessage:
    def __init__(
        self,
        agent: CompiledStateGraph,
        save_or_update_chat_id: SaveOrUpdateChatIdToChannelType,
    ):
        self._agent = agent
        self._save_or_update_chat_id = save_or_update_chat_id

    async def handle(self, update: Update, _context) -> None:
        await self._save_or_update_chat_id.save_or_update(
            channel_type=CHANNEL_TYPE,
            chat_id=str(update.effective_chat.id),
        )

        config = {"configurable": {"thread_id": str(update.effective_user.id)}}
        text = update.message.text

        state = await self._agent.aget_state(config)
        is_paused = any(task.interrupts for task in state.tasks)

        if is_paused:
            graph_input = Command(resume=text)
        else:
            graph_input = {"messages": [HumanMessage(content=text)]}

        result = await self._agent.ainvoke(graph_input, config=config)

        interrupts = result.get("__interrupt__")
        if interrupts:
            content = interrupts[0].value["question"]
        else:
            content = result["messages"][-1].content

        for message in split_message(text=content, max_length=4096):
            await update.message.reply_text(message)
