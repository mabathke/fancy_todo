from __future__ import annotations

from datetime import date
from enum import Enum

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class RecurrenceType(str, Enum):
    NONE = "none"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    # The currently scheduled due date (for one-time and recurring).
    # For one-time: set to NULL when completed/closed (simple "active" filter).
    next_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    recurrence_type: Mapped[RecurrenceType] = mapped_column(
        SAEnum(RecurrenceType, name="recurrence_type"),
        nullable=False,
        default=RecurrenceType.NONE,
    )
    interval: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    completions: Mapped[list["TodoCompletion"]] = relationship(
        back_populates="todo",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class TodoCompletion(Base):
    __tablename__ = "todo_completions"
    __table_args__ = (
        # One completion per todo per scheduled due date (cycle)
        UniqueConstraint("todo_id", "actual_due_date", name="uq_todo_actual_due_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    todo_id: Mapped[int] = mapped_column(
        ForeignKey("todos.id", ondelete="CASCADE"), nullable=False
    )

    # Scheduled due date of the cycle that got completed
    actual_due_date: Mapped[date] = mapped_column(Date, nullable=False)

    # When it was actually finished
    finished_date: Mapped[date] = mapped_column(Date, nullable=False)

    finished_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    todo: Mapped[Todo] = relationship(back_populates="completions")
