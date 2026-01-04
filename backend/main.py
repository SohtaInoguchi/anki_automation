from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from anki_automation import generate_anki_cards, _default_image_dir


app = FastAPI()

# ---- CORS (required for browser requests) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "https://anki-automation-psi.vercel.app"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PingRequest(BaseModel):
    message: str

class GenerateCardsRequest(BaseModel):
    words: list[str]
    source: str = "EN"
    target: str = "FR"

@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/ping")
def ping(req: PingRequest):
    return {
        "reply": f"Backend received: {req.message}"
    }


@app.post("/generate-cards")
def generate_cards(req: GenerateCardsRequest):
    """Generate Anki cards with translations and images."""
    try:
        cards = generate_anki_cards(req.words, source=req.source, target=req.target)
        return {
            "success": True,
            "cards": cards
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Serve static images
image_dir = _default_image_dir()
os.makedirs(image_dir, exist_ok=True)
app.mount("/images", StaticFiles(directory=image_dir), name="images")
