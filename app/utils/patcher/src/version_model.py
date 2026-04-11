from datetime import datetime

from sqlmodel import Field, SQLModel


class Version(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    version: int
    applied_at: datetime
