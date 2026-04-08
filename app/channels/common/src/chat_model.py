from sqlmodel import Field, SQLModel


class Chat(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    channel_type: str = Field(unique=True)
    chat_id: str
