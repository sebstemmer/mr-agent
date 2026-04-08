from sqlmodel import Field, SQLModel


class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(unique=True)
    of_interest: bool = Field(default=False)
    link: str | None = Field(default=None)
    summary: str = Field(default="")
