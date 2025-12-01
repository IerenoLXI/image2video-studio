import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables before importing router (router initializes services immediately)
load_dotenv()

from provider_router import router

app = FastAPI()

default_allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "https://image2video-studio.onrender.com",
]

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
allowed_origins = [
    origin.strip().rstrip("/")
    for origin in allowed_origins_env.split(",")
    if origin.strip()
] or default_allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include provider router
app.include_router(router)

@app.get("/api/health")
async def health():
    return {"status": "ok"}

