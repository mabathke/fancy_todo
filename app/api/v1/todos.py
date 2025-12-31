from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoOut
from app.services.todo_service import TodoService, TodoValidationError

router = APIRouter(prefix="/v1/todos", tags=["todos"])

@router.get("")
def list_todos(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    base_q = db.query(Todo)

    total = base_q.count()
    skip = (page - 1) * page_size

    todos = (
        base_q
        .order_by(Todo.created_at.desc())
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
        "todos": [
            {
                "id": todo.id,
                "title": todo.title,
                "is_completed": bool(todo.is_completed),
                "recurrence_type": todo.recurrence_type,
                "interval": todo.interval,
                "start_date": todo.start_date,
                "created_at": todo.created_at,
            }
            for todo in todos
        ],
    }
    
@router.post("", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    service = TodoService(db)
    try:
        todo = service.create(payload)
    except TodoValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TodoOut(
        id=todo.id,
        title=todo.title,
        created_at=todo.created_at,
        recurrence_type=todo.recurrence_type,
        interval=todo.interval,
        start_date=todo.start_date,
        is_completed=bool(todo.is_completed),
        completed_at=todo.completed_at,
    )