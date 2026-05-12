from agent.agent.src.state.agent_state import State


class UnexpectedStateError(Exception):
    def __init__(self, expected: type[State], actual: State):
        super().__init__(f"Expected {expected.__name__}, got {type(actual).__name__}")
