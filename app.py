from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

class AnalyzeRequest(BaseModel):
    image_base64: str
    prompt: str
    image2_base64: str = None

@app.get("/")
defroot():
    return {"status": "Gemini Live Agent Backend is running"}

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")
    parts = [
        {"text": req.prompt},
        {"inline_data": {"mime_type": "image/jpeg", "data": req.image_base64}}
    ]
   : if req.image2_base64
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": req.image2_base64}})
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048}
    }
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(GEMINI_URL, json=payload)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        data = res.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return {"result": text, "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}
