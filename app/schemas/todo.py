from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field

from app.models.todo import RecurrenceType


class TodoCreate(BaseModel):
    title: str = Field(min_length=1)

    recurrence_type: RecurrenceType = RecurrenceType.NONE
    interval: int = Field(default=1, ge=1)

    next_due_date: date | None = Field(
        default=None,
        description="Next scheduled due date (YYYY-MM-DD). For one-time todos, this is the due date.",
        examples=["2028-12-29"],
    )


class TodoOut(BaseModel):
    id: int
    title: str
    created_at: date

    recurrence_type: RecurrenceType
    interval: int
    next_due_date: date | None

    created_by_id: int | None = Field(
        default=None,
        description="ID of the user who created the todo",
        example=1,
    )

    class Config:
        use_enum_values = True

class TodoCompletionOut(BaseModel):
    id: int
    todo_id: int
    actual_due_date: date
    finished_date: date
    finished_by_id: int | None