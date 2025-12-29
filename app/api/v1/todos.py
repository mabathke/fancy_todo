from fastapi import APIRouter, Depends
import sqlite3

from app.core.db import get_db

router = APIRouter(prefix="/v1/todos", tags=["todos"])


@router.get("")
def list_todos(db: sqlite3.Connection = Depends(get_db)):
    # no logic yet, just proving wiring works
    return {
        "todos": [],
        "message": "Todo endpoint is wired correctly"
    }