import json, uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .config import settings
from .core.brain import PixelBrain
from .documents import extract_text
from .vision import describe_image
from .plugins import PluginManager

app=FastAPI(title="PIXEL AI",version="3.0.0",description="Local-first modular assistant")
brain=PixelBrain()
plugin_manager=PluginManager()

class ChatRequest(BaseModel):
    message:str=Field(min_length=1,max_length=20000)
    session_id:str=Field(default="default",min_length=1,max_length=100)
    temperature:float=Field(default=0.7,ge=0,le=2)
    use_tools:bool=True
class LearnRequest(BaseModel):
    text:str=Field(min_length=1,max_length=100000)
    source:str=Field(default="user",max_length=500)
    category:str=Field(default="general",max_length=100)
    importance:int=Field(default=3,ge=1,le=5)
class MemoryUpdate(BaseModel):
    text:str|None=Field(default=None,max_length=100000)
    category:str|None=Field(default=None,max_length=100)
    importance:int|None=Field(default=None,ge=1,le=5)
class ToolRequest(BaseModel):
    name:str
    arguments:dict={}
class SearchRequest(BaseModel):
    query:str=Field(min_length=1,max_length=1000)
    max_results:int=Field(default=5,ge=1,le=10)

@app.get("/")
def root(): return {"name":"PIXEL","version":"3.0.0","status":"online"}
@app.get("/health")
def health(): return brain.health()
@app.get("/api/settings")
def get_settings():
    return {"version":"3.0.0","model":settings.model_name,"web_search_enabled":settings.web_search_enabled,
            "vision_configured":bool(settings.vision_api_url and settings.vision_model),
            "tool_count":len(brain.tools.list_tools())}
@app.post("/chat")
def chat(request:ChatRequest):
    try: return brain.ask(request.message,request.session_id,request.temperature,request.use_tools)
    except ValueError as exc: raise HTTPException(400,str(exc))
    except Exception as exc: raise HTTPException(500,f"Chat failed: {exc}")
@app.post("/chat/stream")
def chat_stream(request:ChatRequest):
    # The model backend currently generates a complete answer first; chunks are then streamed over SSE.
    def events():
        try:
            result=brain.ask(request.message,request.session_id,request.temperature,request.use_tools)
            for start in range(0,len(result["answer"]),32):
                yield "data: "+json.dumps({"token":result["answer"][start:start+32]},ensure_ascii=False)+"\n\n"
            yield "data: "+json.dumps({"done":True,"meta":{k:v for k,v in result.items() if k!="answer"}},ensure_ascii=False)+"\n\n"
        except Exception as exc:
            yield "data: "+json.dumps({"error":str(exc)},ensure_ascii=False)+"\n\n"
    return StreamingResponse(events(),media_type="text/event-stream",headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})
@app.post("/learn")
def learn(req:LearnRequest):
    try: return brain.learn(req.text,req.source,req.category,req.importance)
    except ValueError as exc: raise HTTPException(400,str(exc))
@app.get("/memory")
def memories(limit:int=Query(default=100,ge=1,le=1000)): return {"items":brain.memories(limit)}
@app.get("/memory/search")
def memory_search(q:str=Query(min_length=1),limit:int=Query(default=5,ge=1,le=50)):
    return {"query":q,"items":brain.search_memory(q,limit)}
@app.patch("/memory/{memory_id}")
def memory_update(memory_id:int,req:MemoryUpdate):
    result=brain.update_memory(memory_id,**req.model_dump(exclude_unset=True))
    if result["status"]=="not_found": raise HTTPException(404,"Memory not found")
    return result
@app.delete("/memory/{memory_id}")
def memory_delete(memory_id:int):
    result=brain.forget(memory_id)
    if result["status"]=="not_found": raise HTTPException(404,"Memory not found")
    return result
@app.get("/sessions")
def sessions(): return {"items":brain.sessions()}
@app.delete("/sessions/{session_id}")
def session_delete(session_id:str):
    if len(session_id)>100: raise HTTPException(400,"Invalid session ID")
    return brain.delete_session(session_id)
@app.delete("/chat/{session_id}")
def chat_clear(session_id:str): return brain.clear_chat(session_id)
@app.get("/tools")
def tools(): return {"items":brain.tools.list_tools()}
@app.post("/tools/run")
def tool_run(req:ToolRequest):
    result=brain.orchestrator.run_tool(req.name,**req.arguments)
    if not result.get("success",False): raise HTTPException(400,result.get("error","Tool failed"))
    return result
@app.post("/search")
def web_search(req:SearchRequest):
    if not settings.web_search_enabled: raise HTTPException(403,"Web search disabled in .env")
    result=brain.orchestrator.run_tool("web_search",query=req.query,max_results=req.max_results)
    if not result.get("success"): raise HTTPException(503,result.get("error","Search failed"))
    return result
@app.post("/files/read")
async def read_file(file:UploadFile=File(...), remember:bool=Form(False)):
    data=await file.read()
    try: text=extract_text(file.filename or "upload.txt",data)
    except ValueError as exc: raise HTTPException(400,str(exc))
    if remember and text: brain.learn(text[:100000],source=file.filename or "upload",category="document",importance=3)
    return {"filename":file.filename,"characters":len(text),"text":text[:200000],"truncated":len(text)>200000}
@app.post("/vision")
async def vision(file:UploadFile=File(...),prompt:str=Form("Describe this image.")):
    name=file.filename or "image.png"
    if Path(name).suffix.lower() not in {".png",".jpg",".jpeg",".webp",".gif"}: raise HTTPException(400,"Upload a PNG, JPG, WEBP, or GIF image.")
    data=await file.read()
    if len(data)>12*1024*1024: raise HTTPException(413,"Image exceeds 12 MB limit.")
    result=describe_image(name,data,prompt)
    if not result.get("success"): raise HTTPException(503,result.get("error","Vision unavailable"))
    return result
@app.get("/plugins")
def plugins(): return {"items":plugin_manager.discover()}
@app.get("/dashboard")
def dashboard():
    return {"memory_count":len(brain.memories(100000)),"sessions":len(brain.sessions()),
            "tools":len(brain.tools.list_tools()),"model":brain.model.info()}

WEB=Path(__file__).resolve().parent.parent/"web"
app.mount("/static",StaticFiles(directory=WEB),name="static")
@app.get("/app",include_in_schema=False)
def frontend(): return FileResponse(WEB/"index.html")
