from sqlmodel import Field, SQLModel


class File(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(unique=True, index=True)
    filename: str
    filetype: str
