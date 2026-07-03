"""Thin API wrapper around the cascade router.

Run: uvicorn service.app:app --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI
from pydantic import BaseModel

from router.cascade import route

app = FastAPI(title="Hybrid Token-Efficient Routing Agent")


class TaskRequest(BaseModel):
    prompt: str


@app.post("/answer")
def answer(req: TaskRequest):
    return route(req.prompt)


@app.get("/health")
def health():
    return {"status": "ok"}
