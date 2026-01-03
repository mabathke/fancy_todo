from __future__ import annotations

from datetime import datetime, timezone, date, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.todo import Todo, TodoCompletion, RecurrenceType
from app.schemas.todo import TodoCreate


class TodoValidationError(ValueError):
    pass


def utc_today() -> date:
    return datetime.now(timezone.utc).date()


def validate_due_date(next_due_date: date | None) -> None:
    if next_due_date is None:
        return
    if next_due_date < utc_today():
        raise TodoValidationError("next_due_date cannot be in the past")


def add_months(d: date, months: int) -> date:
    # minimal “no extra deps” month add:
    # move to first of month, shift, then clamp day
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1

    # clamp day to last day of target month
    # compute last day: go to 1st of next month - 1 day
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day = (next_month - timedelta(days=1)).day

    day = min(d.day, last_day)
    return date(year, month, day)


def advance_due_date(current_due: date, recurrence_type: RecurrenceType, interval: int) -> date:
    if interval < 1:
        raise TodoValidationError("interval must be >= 1")

    if recurrence_type == RecurrenceType.WEEKLY:
        return current_due + timedelta(days=7 * interval)
    if recurrence_type == RecurrenceType.MONTHLY:
        return add_months(current_due, interval)

    raise TodoValidationError("Cannot advance due date for recurrence_type=NONE")


class TodoService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: TodoCreate, user_id: int) -> Todo:
        validate_due_date(payload.next_due_date)

        todo = Todo(
            title=payload.title.strip(),
            created_at=utc_today(),
            recurrence_type=payload.recurrence_type,
            interval=payload.interval,
            next_due_date=payload.next_due_date,
            created_by_id=user_id,
        )

        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def complete(self, todo_id: int, current_user_id: int) -> Todo:
        todo: Todo | None = self.db.query(Todo).filter(Todo.id == todo_id).first()
        if not todo:
            raise TodoValidationError("Todo not found")

        if todo.next_due_date is None:
            raise TodoValidationError("Todo has no active due date to complete")

        completion = TodoCompletion(
            todo_id=todo.id,
            actual_due_date=todo.next_due_date,
            finished_date=utc_today(),
            finished_by_id=current_user_id,
        )
        self.db.add(completion)

        try:
            # commit completion first to catch unique constraint violation
            self.db.flush()
        except IntegrityError:
            self.db.rollback()
            raise TodoValidationError("Todo already completed for this period")

        # Now update the todo schedule
        if todo.recurrence_type == RecurrenceType.NONE:
            todo.next_due_date = None  # closed
        else:
            todo.next_due_date = advance_due_date(
                todo.next_due_date,
                todo.recurrence_type,
                todo.interval,
            )

        self.db.commit()
        self.db.refresh(todo)
        return todo

    def uncomplete(self, todo_completion_id: int) -> TodoCompletion:
        completion: TodoCompletion | None = (
            self.db.query(TodoCompletion)
            .filter(TodoCompletion.id == todo_completion_id)
            .first()
        )
        if not completion:
            raise TodoValidationError("Completed todo not found")

        self.db.delete(completion)
        self.db.commit()
        return completion
