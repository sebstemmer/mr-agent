from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

from agent_v2.agent.src.state.agent_state import AgentState, NewMessageAction, BaseState


class HandleIncomingMessage:
    def __init__(self, agent: CompiledStateGraph):
        self._agent = agent

    async def handle(self, chat_id: str, text: str) -> None:
        config: RunnableConfig = {"configurable": {"thread_id": chat_id}}

        state = await self._agent.aget_state(config)
        print("state", state)
        is_paused = any(task.interrupts for task in state.tasks)

        if is_paused:
            graph_input: Command = Command(resume=text)
        elif state.values.get("state") is None:
            graph_input: AgentState = {
                "state": BaseState(messages=[HumanMessage(content=text)])
            }
        else:
            graph_input: AgentState = {
                "state": NewMessageAction(message=HumanMessage(content=text))
            }

        result: AgentState = await self._agent.ainvoke(input=graph_input, config=config)

        interrupts = result.get("__interrupt__")
        if interrupts:
            content = interrupts[0].value["question"]
        else:
            content = result["state"].messages[-1].content

        # for message in split_message(text=content, max_length=4096):
        #    await update.message.reply_text(message)
