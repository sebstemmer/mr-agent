from sqlmodel import Field, SQLModel


class JobOpening(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    summary: str
    requirements: str
    link_to_company: str | None = Field(default=None)
