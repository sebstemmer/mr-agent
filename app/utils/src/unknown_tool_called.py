class UnknownToolCalled(ValueError):
    def __init__(self, tool_name: str):
        super().__init__(
            f"The LLM called tool '{tool_name}', but no handler is registered for it."
        )
