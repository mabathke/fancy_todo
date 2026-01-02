from fastapi import FastAPI
from app.api.v1.todos import router as todos_router
from app.api.v1.auth import router as auth_router

app = FastAPI(title="Todo Backend")
app.include_router(todos_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"status": "ok"}
