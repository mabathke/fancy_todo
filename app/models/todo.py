from __future__ import annotations

from datetime import date
from enum import Enum

from sqlalchemy import Date, ForeignKey, Integer, String, Text, UniqueConstraint
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
    created_at: Mapped[str] = mapped_column(Text, nullable=False)

    recurrence_type: Mapped[RecurrenceType] = mapped_column(
        SAEnum(RecurrenceType, name="recurrence_type"),
        nullable=False,
        default=RecurrenceType.NONE,
    )
    interval: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    completions: Mapped[list["TodoCompletion"]] = relationship(
        back_populates="todo",
        cascade="all, delete-orphan",
    )


class TodoCompletion(Base):
    __tablename__ = "todo_completions"
    __table_args__ = (UniqueConstraint("todo_id", "period_key", name="uq_todo_period"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    todo_id: Mapped[int] = mapped_column(
        ForeignKey("todos.id", ondelete="CASCADE"), nullable=False
    )

    period_key: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # '2026-W01', '2026-01', NULL for one-time
    completed_at: Mapped[date] = mapped_column(Date, nullable=False)

    todo: Mapped[Todo] = relationship(back_populates="completions")
