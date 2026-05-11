from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, Interrupt

from agent_v2.agent.src.message_sender import MessageSender
from agent_v2.agent.src.state.agent_state import AgentState, BaseState, NewMessageAction


class HandleIncomingMessage:
    def __init__(self, agent: CompiledStateGraph, send_message: MessageSender):
        self._agent = agent
        self._send_message = send_message

    async def handle(self, chat_id: str, text: str) -> None:
        config: RunnableConfig = {"configurable": {"thread_id": chat_id}}

        state = await self._agent.aget_state(config)
        pending_interrupts = [
            interrupt for task in state.tasks for interrupt in task.interrupts
        ]

        if pending_interrupts:
            answers = [a.strip() for a in text.split(",")]
            if len(answers) != len(pending_interrupts):
                await self._send_message.send(
                    message=f"Expected {len(pending_interrupts)} answers, got {len(answers)}. Please answer again.",
                )
                return
            resume_map = {
                interrupt.id: answer
                for interrupt, answer in zip(pending_interrupts, answers)
            }
            graph_input: Command = Command(resume=resume_map)
        elif state.values.get("state") is None:
            graph_input: AgentState = {
                "state": BaseState(messages=[HumanMessage(content=text)])
            }
        else:
            graph_input: AgentState = {
                "state": NewMessageAction(message=HumanMessage(content=text))
            }

        result: AgentState = await self._agent.ainvoke(input=graph_input, config=config)

        interrupts: list[Interrupt] | None = result.get("__interrupt__")
        if interrupts:
            await self._send_message.send(
                message=self._format_interrupt_message(interrupts=interrupts),
            )

    @staticmethod
    def _format_interrupt_message(interrupts: list[Interrupt]) -> str:
        if len(interrupts) == 1:
            return f"{interrupts[0].value['question']} (y/n)"

        lines = [
            f"{i}. {interrupt.value['question']}"
            for i, interrupt in enumerate(interrupts, start=1)
        ]
        example = ",".join("y" if i % 2 == 0 else "n" for i in range(len(interrupts)))
        lines.append(
            f"\nAnswer with {len(interrupts)} comma-separated values, e.g. {example}"
        )
        return "\n".join(lines)
