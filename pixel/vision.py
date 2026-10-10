import base64, json, urllib.request
from .config import settings

def describe_image(filename: str, data: bytes, prompt: str="Describe this image."):
    """Optional OpenAI-compatible vision endpoint; does not pretend the text-only local model can see."""
    if not (settings.vision_api_url and settings.vision_model):
        return {"success":False,"error":"Vision is not configured. Set PIXEL_VISION_API_URL and PIXEL_VISION_MODEL in .env to an OpenAI-compatible vision endpoint."}
    import mimetypes
    mime=mimetypes.guess_type(filename)[0] or "application/octet-stream"
    payload={"model":settings.vision_model,"messages":[{"role":"user","content":[
        {"type":"text","text":prompt},
        {"type":"image_url","image_url":{"url":f"data:{mime};base64,{base64.b64encode(data).decode()}"}}
    ]}],"max_tokens":600}
    req=urllib.request.Request(settings.vision_api_url.rstrip("/")+"/chat/completions",
        data=json.dumps(payload).encode(),headers={"Content-Type":"application/json",
        **({"Authorization":"Bearer "+settings.vision_api_key} if settings.vision_api_key else {})},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=90) as response: result=json.loads(response.read())
        return {"success":True,"answer":result["choices"][0]["message"]["content"]}
    except Exception as exc: return {"success":False,"error":f"Vision request failed: {exc}"}
