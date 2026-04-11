from datetime import date

from sqlmodel import Field, SQLModel


class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    public_id: str = Field(unique=True, index=True)
    job_id: str = Field(unique=True)
    of_interest: bool = Field(default=False)
    liked_by_user: bool | None = Field(default=None)
    link: str | None = Field(default=None)
    summary: str = Field(default="")
    created_at: date = Field(default_factory=date.today)
