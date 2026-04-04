from contextlib import asynccontextmanager

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from fastapi import FastAPI
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langgraph.prebuilt import ToolNode
from typing import Annotated
from langgraph.graph import add_messages
from langgraph.checkpoint.memory import MemorySaver
from datetime import date

from config import settings
from container import Container
from tools.weather import get_weather
from channels.src.split_message import split_message

container = Container()

telegram_app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

tools = [get_weather, container.jobs_tool(), container.job_search_status_tool()]

llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-5.4-mini")
llm_with_tools = llm.bind_tools(tools)

memory = MemorySaver()


@asynccontextmanager
async def lifespan(_app):
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()  # type: ignore

    yield

    await telegram_app.updater.stop()  # type: ignore
    await telegram_app.stop()
    await telegram_app.shutdown()


app = FastAPI(lifespan=lifespan)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def log_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = await agent.ainvoke({"messages": [HumanMessage(content=update.message.text)]},
                                 config={"configurable": {"thread_id": str(update.effective_user.id)}})
    content = result["messages"][-1].content
    for message in split_message(content):
        await update.message.reply_text(message)


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return "end"


async def llm_node(state: AgentState):
    print(state["messages"])
    system = SystemMessage(
        content=f"You are a helpful assistant. Today's date is {date.today()}.")
    response = await llm_with_tools.ainvoke([system] + state["messages"])
    return {"messages": [response]}


tool_node = ToolNode(tools)

graph = StateGraph(AgentState)
graph.add_node("llm", llm_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "llm")
graph.add_conditional_edges("llm", should_continue, {"tools": "tools", "end": END})
graph.add_edge("tools", "llm")
agent = graph.compile(checkpointer=memory)

telegram_app.add_handler(CommandHandler("hello", hello))
telegram_app.add_handler(MessageHandler(filters.TEXT, log_input))
