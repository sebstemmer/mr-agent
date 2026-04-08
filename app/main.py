from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated, TypedDict

from container import Container
from dependency_injector import providers
from fastapi import FastAPI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode
from sqlmodel import SQLModel
from tools.weather import get_weather
from utils.src.config import settings

container = Container()

tools = [get_weather, container.jobs_tool(), container.job_search_status_tool()]

llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-5.4-mini")
llm_with_tools = llm.bind_tools(tools)

memory = MemorySaver()


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
        content=f"You are a helpful assistant. Today's date is {date.today()}."
    )
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

container.agent.override(providers.Object(agent))


@asynccontextmanager
async def lifespan(_app):
    async with container.utils().engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    scheduler = container.utils().scheduler()
    scheduler.start()

    telegram_bot = container.telegram().bot()
    await telegram_bot.start()

    yield

    scheduler.shutdown()
    await telegram_bot.stop()


app = FastAPI(lifespan=lifespan)
