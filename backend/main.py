import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY not found in .env. Add it to your project root .env file.")

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Paths
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))  # museai/
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Serve index.html


@app.get("/")
async def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Serve JS manually


@app.get("/script.js")
async def serve_js():
    return FileResponse(os.path.join(FRONTEND_DIR, "script.js"))

# Serve CSS manually


@app.get("/style.css")
async def serve_css():
    return FileResponse(os.path.join(FRONTEND_DIR, "style.css"))

# ---- API routes


@app.get("/models")
async def get_models():
    return [
        {"id": "openrouter/auto", "name": "OpenRouter Auto"},
        {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini"},
        {"id": "openai/gpt-4o", "name": "GPT-4o"},
        {"id": "mistralai/mistral-7b-instruct", "name": "Mistral 7B Instruct"}
    ]


@app.post("/generate")
async def generate(request: Request):
    body = await request.json()
    model = body.get("model") or "openrouter/auto"
    prompt = (body.get("prompt") or "").strip()

    if not prompt:
        return JSONResponse({"error": "Prompt is required."}, status_code=400)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "MuseAI",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are MuseAI, a concise and helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )

        if r.status_code != 200:
            return JSONResponse(
                {"error": f"OpenRouter error {r.status_code}: {r.text}"},
                status_code=r.status_code
            )

        data = r.json()
        text = data.get("choices", [{}])[0].get("message", {}).get(
            "content", "").strip() or "(empty response)"
        return {"response": text}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
