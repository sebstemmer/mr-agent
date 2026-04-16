from typing import Generic, TypeVar

T = TypeVar("T")


class UpdateField(Generic[T]):
    pass


class StaysTheSame(UpdateField[T]):
    pass


class Update(UpdateField[T]):
    def __init__(self, value: T):
        self.value = value
