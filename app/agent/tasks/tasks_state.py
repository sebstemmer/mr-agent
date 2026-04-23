from agent.common.sequential_tool_execution_state import (
    SequentialToolExecutionState,
    SequentialToolExecutionStateType,
    parse_sequential_tool_execution_state,
)
from agent.state.agent_state import AgentState

TASKS_SEQUENTIAL_TOOL_EXECUTION_STATE_KEY = "tasks_sequential_tool_execution_state"


class TasksState(AgentState):
    tasks_sequential_tool_execution_state: SequentialToolExecutionState


def get_tasks_sequential_tool_execution_state(
    tasks_state: TasksState, expected_type: type[SequentialToolExecutionStateType]
) -> SequentialToolExecutionStateType:
    return parse_sequential_tool_execution_state(
        sequential_tool_execution_state=get_tasks_sequential_tool_execution_state_or_none(
            tasks_state=tasks_state,
        ),
        expected_type=expected_type,
    )


def get_tasks_sequential_tool_execution_state_or_none(
    tasks_state: TasksState,
) -> SequentialToolExecutionState | None:
    return tasks_state.get(TASKS_SEQUENTIAL_TOOL_EXECUTION_STATE_KEY)
