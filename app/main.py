# app/main.py
from fastapi import FastAPI
from app.api.v1.todos import router as todos_router

app = FastAPI(title="Todo Backend")

app.include_router(todos_router)


@app.get("/")
def root():
    return {"status": "ok"}
