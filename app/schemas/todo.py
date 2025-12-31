from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.models.todo import RecurrenceType


class TodoCreate(BaseModel):
    title: str = Field(min_length=1)

    recurrence_type: RecurrenceType = RecurrenceType.NONE
    interval: int = Field(default=1, ge=1)
    start_date: date | None = Field(
        default=None,
        description="ISO date in YYYY-MM-DD",
        examples=["2028-12-29"],
    )


class TodoOut(BaseModel):
    id: int
    title: str
    created_at: date

    recurrence_type: RecurrenceType
    interval: int
    start_date: date | None = Field(
        default=None,
        description="ISO date in YYYY-MM-DD",
        examples=["2028-12-29"],
    )

    is_completed: bool
    completed_at: date | None

    class Config:
        use_enum_values = True
