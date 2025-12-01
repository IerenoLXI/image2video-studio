## Image2Video Studio

Image2Video Studio combines a FastAPI backend with a React frontend that turns a still image (or preset avatar) plus text into a short talking-head video using third‑party providers such as HeyGen, D‑ID, and A2E.

### Features
- Simple web UI for uploading or linking an image, entering narration text, and selecting a provider.
- FastAPI backend that normalizes start/status calls across providers and serves uploaded assets locally.
- Ready-to-use scripts for launching backend and frontend together on Windows.
- Render deployment guide for hosting just the backend.

### Repository Layout
```
.
├── backend/           # FastAPI app, provider routers, service clients
├── frontend/          # React/Vite UI
├── README-RUN.md      # Detailed local run instructions & troubleshooting
├── README_deploy.md   # Render deployment walkthrough
├── start-project.*    # Convenience scripts to run both servers
└── README.md          # You are here
```

### Prerequisites
- Python 3.11+ with `venv` (backend)
- Node.js 18+ and npm (frontend)
- Provider API keys:
  - `A2E_TOKEN`
  - `DID_KEY`
  - `HEYGEN_KEY` (+ optional `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID`, etc.)

Store these values in a `.env` file at the repo root (loaded by `backend/main.py`) or set them via your shell / hosting provider. See `README_deploy.md` for the minimum variables required in production.

### Quick Start
For the fastest Windows workflow, double-click `start-project.bat` or run `start-project.ps1` to boot both servers. Full step-by-step backend/frontend instructions plus troubleshooting tips live in `README-RUN.md`.

Key endpoints once running locally:
- UI: http://localhost:3000
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

### Provider Notes
- Each provider implementation resides in `backend/services/*_service.py`.
- The HeyGen integration calls `https://api.heygen.com/v2/video/generate` with `X-Api-Key` authentication and exposes a diagnostic helper at `POST /api/heygen/test-call` for verifying endpoint/status responses.
- No provider credentials are bundled with the repo; make sure to set the required env vars before using the respective dropdown option in the UI.

### Contributing
1. Create a virtual environment (`python -m venv backend/venv`) and install backend deps via `pip install -r backend/requirements.txt`.
2. From `frontend/`, run `npm install`.
3. Use `npm run dev` (frontend) and `uvicorn main:app --reload` (backend) during development, or rely on the provided helper scripts.
4. Submit pull requests against `main`; please lint/format and add tests where applicable.


