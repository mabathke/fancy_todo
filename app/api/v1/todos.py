from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.core.db import get_db
from app.models.todo import Todo, TodoCompletion
from app.models.user import User
from app.schemas.todo import TodoCompletionOut, TodoCreate, TodoOut
from app.services.todo_service import TodoService, TodoValidationError

router = APIRouter(prefix="/v1/todos", tags=["todos"])


@router.get("")
def list_todos(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = db.query(Todo)


    total = query.count()
    skip = (page - 1) * page_size

    todos = query.order_by(Todo.created_at.desc()).offset(skip).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "todos": [
            {
                "id": todo.id,
                "title": todo.title,
                "created_at": todo.created_at,
                "next_due_date": todo.next_due_date,
                "recurrence_type": todo.recurrence_type,
                "interval": todo.interval,
                "created_by_id": todo.created_by_id,
                }
            for todo in todos
        ],
    }


@router.get("/completed_todos")
def list_completed_todos(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = db.query(TodoCompletion)

    total = query.count()
    skip = (page - 1) * page_size

    completed_todos = (
        query.order_by(TodoCompletion.finished_date.desc())
        .offset(skip)
        .limit(page_size)
        .all()
    )

    total_pages = (total + page_size - 1) // page_size

    return {
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "completed_todos": [
            {
                "id": completed.id,
                "todo_id": completed.todo_id,
                "actual_due_date": completed.actual_due_date,
                "finished_date": completed.finished_date,
                "finished_by_id": completed.finished_by_id,
            }
            for completed in completed_todos
        ],
    }


@router.post("", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(
    payload: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TodoService(db)
    try:
        todo = service.create(payload, current_user.id)
        return TodoOut(
            id=todo.id,
            title=todo.title,
            created_at=todo.created_at,
            next_due_date=todo.next_due_date,
            recurrence_type=todo.recurrence_type,
            interval=todo.interval,
            created_by_id=todo.created_by_id,
        )
    except TodoValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{todo_id}/complete", response_model=TodoOut)
def complete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TodoService(db)
    try:
        todo = service.complete(todo_id, current_user.id)
        return TodoOut(
            id=todo.id,
            title=todo.title,
            created_at=todo.created_at,
            next_due_date=todo.next_due_date,
            recurrence_type=todo.recurrence_type,
            interval=todo.interval,
            created_by_id=todo.created_by_id,
        )
    except TodoValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/completions/{completion_id}", response_model=TodoCompletionOut)
def uncomplete_todo(
    completion_id: int,
    db: Session = Depends(get_db),
):
    service = TodoService(db)
    try:
        completion = service.uncomplete(completion_id)
        return TodoCompletionOut(
            id=completion.id,
            todo_id=completion.todo_id,
            actual_due_date=completion.actual_due_date,
            finished_date=completion.finished_date,
            finished_by_id=completion.finished_by_id,
        )
    except TodoValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
