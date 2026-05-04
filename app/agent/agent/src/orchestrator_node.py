from enum import Enum
from logging import Logger

from pydantic import BaseModel
from utils.common.src.llm_builder import LlmBuilder

from agent.job_search.src.handle_job_search_node import JOB_SEARCH_BRANCH
from agent.state.agent_state import (
    AgentState,
    Branch,
    DecidedForBranchesAction,
    DecidedForTextResponseAction,
)
from agent.tasks.create_tasks_subgraph import PERSONAL_TASK_LIST_BRANCH
from agent.weather.src.handle_weather_node import HANDLE_WEATHER_NODE_NAME


class OrchestratorOption(str, Enum):
    SUBTASKS = "subtasks"
    TEXT_RESPONSE = "text_response"


class OrchestratorDecision(BaseModel):
    option: OrchestratorOption
    subtasks: list[Branch] | None = None
    text_response: str | None = None


class OrchestratorNode:
    _ADDITIONAL_INSTRUCTION = (
        "You are an orchestrator that decides how to handle the user's message."
        " You have two options:\n"
        "1. Respond with a list of subtasks to dispatch."
        " You may select multiple subtasks when the request spans different domains"
        " (e.g. 'What's the weather in Berlin and show me my tasks'),"
        " but each subtask may only appear once.\n"
        "2. Respond with a text message directly if no subtask is needed"
        " (e.g. greetings, general questions, chitchat).\n"
        "\n"
        "Available subtasks:\n"
        f"- {HANDLE_WEATHER_NODE_NAME}: Handles weather-related questions.\n"
        f"- {JOB_SEARCH_BRANCH}: Handles job search related questions.\n"
        f"- {PERSONAL_TASK_LIST_BRANCH}: The user's personal task list."
        " Supports adding, reading, updating, completing, and deleting tasks."
    )

    def __init__(
        self,
        api_key: str,
        model: str,
        logger: Logger,
    ):
        self._llm = (
            LlmBuilder(api_key=api_key, model=model)
            .instruction(OrchestratorNode._ADDITIONAL_INSTRUCTION)
            .structured_output(schema=OrchestratorDecision)
            .build()
        )
        self._logger = logger

    async def orchestrate(self, state: AgentState) -> dict:
        decision: OrchestratorDecision = await self._llm.ainvoke_structured(
            messages=state["messages"],
        )

        self._logger.info("decision=%s", decision)

        if decision.option == OrchestratorOption.TEXT_RESPONSE:
            return self._handle_text_response(decision=decision)

        if decision.option == OrchestratorOption.SUBTASKS:
            return self._handle_subtasks(decision=decision)

        raise ValueError(f"Unhandled option: {decision.option}")

    def _handle_text_response(self, decision: OrchestratorDecision) -> dict:
        if decision.subtasks is not None:
            self._logger.warning(
                "text_response selected but subtasks is not None: %s",
                decision.subtasks,
            )
        return {
            "orchestrator_decision": DecidedForTextResponseAction(
                logger=self._logger, text_response=decision.text_response
            )
        }

    def _handle_subtasks(self, decision: OrchestratorDecision) -> dict:
        if decision.text_response is not None:
            self._logger.warning(
                "subtasks selected but text_response is not None: %s",
                decision.text_response,
            )

        deduplicated = list(dict.fromkeys(decision.subtasks))
        if len(deduplicated) != len(decision.subtasks):
            self._logger.warning("duplicate subtasks=%s", decision.subtasks)

        return {
            "orchestrator_decision": DecidedForBranchesAction(
                logger=self._logger, branches=deduplicated
            )
        }
