from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# UNCOMMENT AFTER generate_anki_cards is difined
# from backend.anki_automation import generate_anki_cards


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

@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/ping")
def ping(req: PingRequest):
    return {
        "reply": f"Backend received: {req.message}"
    }
