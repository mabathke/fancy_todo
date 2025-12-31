from __future__ import annotations

from datetime import datetime, timezone, date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.todo import Todo, TodoCompletion, RecurrenceType
from app.schemas.todo import TodoCreate


class TodoValidationError(ValueError):
    pass


def validate_start_date(start_date: date | None) -> None:
    if start_date is None:
        return

    today = datetime.now(timezone.utc).date()
    if start_date < today:
        raise TodoValidationError("start_date cannot be in the past")


def period_key_for(todo: Todo, today: date) -> str:
    # IMPORTANT: do NOT use NULL for one-time because UNIQUE(todo_id, NULL)
    # allows multiple rows in SQLite. Use a stable string.
    if todo.recurrence_type == RecurrenceType.NONE:
        return "one-time"
    if todo.recurrence_type == RecurrenceType.WEEKLY:
        iso_year, iso_week, _ = today.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    if todo.recurrence_type == RecurrenceType.MONTHLY:
        return f"{today.year}-{today.month:02d}"
    return "one-time"


class TodoService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: TodoCreate) -> Todo:
        if payload.recurrence_type != RecurrenceType.NONE and not payload.start_date:
            raise TodoValidationError("start_date is required for recurring todos")

        validate_start_date(payload.start_date)

        today = datetime.now(timezone.utc).date()
        
        todo = Todo(
            title=payload.title.strip(),
            created_at=today,
            recurrence_type=payload.recurrence_type,
            interval=payload.interval,
            start_date=payload.start_date,
            is_completed=0,
            completed_at=None,
            due_date=None,
        )

        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def complete(self, todo_id: int) -> Todo:
        todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
        if not todo:
            raise TodoValidationError("Todo not found")

        today = date.today()
        pk = period_key_for(todo, today)

        completion = TodoCompletion(
            todo_id=todo.id,
            period_key=pk,
            completed_at=today,
        )
        self.db.add(completion)

        # Optional convenience fields for list views (current period)
        todo.is_completed = 1
        todo.completed_at = today

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise TodoValidationError("Todo already completed for this period")

        self.db.refresh(todo)
        return todo

    def uncomplete(self, todo_id: int) -> Todo:
        todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
        if not todo:
            raise TodoValidationError("Todo not found")

        today = date.today()
        pk = period_key_for(todo, today)

        completion = (
            self.db.query(TodoCompletion)
            .filter(TodoCompletion.todo_id == todo.id, TodoCompletion.period_key == pk)
            .first()
        )
        if not completion:
            raise TodoValidationError("No completion found for this period")

        self.db.delete(completion)

        # Optional convenience reset for current period
        todo.is_completed = 0
        todo.completed_at = None

        self.db.commit()
        self.db.refresh(todo)
        return todo
