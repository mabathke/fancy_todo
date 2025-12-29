from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.todo import RecurrenceType


class TodoCreate(BaseModel):
    title: str = Field(min_length=1)

    recurrence_type: RecurrenceType = RecurrenceType.NONE
    interval: int = Field(default=1, ge=1)
    start_date: str | None = None


class TodoOut(BaseModel):
    id: int
    title: str
    created_at: str

    recurrence_type: RecurrenceType
    interval: int
    start_date: str | None

    is_completed: bool
    completed_at: str | None

    class Config:
        use_enum_values = True
