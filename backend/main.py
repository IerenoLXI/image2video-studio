from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables before importing router (router initializes services immediately)
load_dotenv()

from provider_router import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include provider router
app.include_router(router)

@app.get("/api/health")
async def health():
    return {"status": "ok"}

