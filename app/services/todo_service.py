from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.todo import Todo, RecurrenceType
from app.schemas.todo import TodoCreate


class TodoValidationError(ValueError):
    pass


class TodoService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: TodoCreate) -> Todo:
        if payload.recurrence_type != RecurrenceType.NONE and not payload.start_date:
            raise TodoValidationError("start_date is required for recurring todos")

        now = datetime.now(timezone.utc).isoformat()

        todo = Todo(
            title=payload.title.strip(),
            created_at=now,
            recurrence_type=payload.recurrence_type,
            interval=payload.interval,
            start_date=payload.start_date,
            is_completed=0,
            completed_at=None,
        )

        self.db.add(todo)
        self.db.flush()
        return todo
