from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from .brain import PixelBrain

app = FastAPI(
    title="PIXEL AI",
    version="2.0.0",
    description="A modular local AI assistant with semantic memory, RAG, sessions, and a REST API.",
)
brain = PixelBrain()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20000)
    session_id: str = Field(default="default", min_length=1, max_length=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class LearnRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100000)
    source: str = Field(default="user", max_length=500)
    category: str = Field(default="general", max_length=100)
    importance: int = Field(default=3, ge=1, le=5)


@app.get("/")
def root():
    return {"name": "PIXEL", "version": "2.0.0", "status": "online"}


@app.get("/health")
def health():
    return brain.health()


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        return brain.ask(request.message, request.session_id, request.temperature)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/learn")
def learn(request: LearnRequest):
    try:
        return brain.learn(request.text, request.source, request.category, request.importance)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/memory")
def list_memory(limit: int = Query(default=50, ge=1, le=500)):
    return {"items": brain.memories(limit)}


@app.get("/memory/search")
def search_memory(q: str = Query(min_length=1), limit: int = Query(default=5, ge=1, le=50)):
    return {"query": q, "items": brain.search(q, limit)}


@app.delete("/memory/{memory_id}")
def delete_memory(memory_id: int):
    result = brain.forget(memory_id)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Memory not found")
    return result


@app.delete("/chat/{session_id}")
def clear_chat(session_id: str):
    return brain.clear_chat(session_id)
