from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# ---- CORS (required for browser requests) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PingRequest(BaseModel):
    message: str

@app.post("/ping")
def ping(req: PingRequest):
    return {
        "reply": f"Backend received: {req.message}"
    }
