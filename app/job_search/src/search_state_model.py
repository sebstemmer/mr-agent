from datetime import date

from sqlmodel import SQLModel, Field

class SearchState(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    last_searched_at: date | None = Field(default=None)
