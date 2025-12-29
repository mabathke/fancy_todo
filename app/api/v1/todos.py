from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db

router = APIRouter(prefix="/v1/todos", tags=["todos"])

@router.get("")
def list_todos(db: Session = Depends(get_db)):
    return {"todos": [], "message": "wired with SQLAlchemy Session"}
