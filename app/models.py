from datetime import date

from sqlmodel import SQLModel, Field


class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(unique=True)
    of_interest: bool = Field(default=False)
    link: str
    is_dead: bool = Field(default=False)
    summary: str = Field(default="")


class SearchState(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    initialized_at: date | None = Field(default=None)
    last_search: date | None = Field(default=None)
