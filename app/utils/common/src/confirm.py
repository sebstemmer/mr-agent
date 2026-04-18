from langgraph.types import interrupt

_ACCEPTED = ("yes", "y")


def confirm(question: str) -> bool:
    answer = interrupt({"question": question})
    return str(answer).strip().lower() in _ACCEPTED
