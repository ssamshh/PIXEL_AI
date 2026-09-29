from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .brain import PixelBrain

app = FastAPI(title="PIXEL AI", version="0.1.0", description="Deep Learning AI with semantic memory and RAG.")
brain = PixelBrain()

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20000)

class LearnRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100000)
    source: str = "user"

@app.get("/")
def root(): return {"name": "PIXEL", "status": "online"}

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/chat")
def chat(request: ChatRequest):
    try: return brain.ask(request.message)
    except Exception as exc: raise HTTPException(status_code=500, detail=str(exc))

@app.post("/learn")
def learn(request: LearnRequest):
    try: return brain.learn(request.text, request.source)
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc))
