from datetime import date

from sqlmodel import Field, SQLModel


class JobOpening(SQLModel, table=True):
    __tablename__ = "job_opening"
    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(unique=True, index=True)
    title: str
    summary: str
    requirements: str
    link_to_company: str | None = Field(default=None)
    rating: int
    rating_reason: str
    applied: bool = Field(default=False)
    applied_at: date | None = Field(default=None)
    asked_salary: str | None = Field(default=None)
    application_file_uuid: str | None = Field(default=None)
