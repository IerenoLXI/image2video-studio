# Deploying the FastAPI Backend on Render

Use this guide to publish only the backend to Render while keeping the React app running locally.

## 1. Prepare the Repository
- Create a new GitHub repository (public or private).
- Initialize Git if needed, add all project files, then commit.
- Push the repository to GitHub so Render can access it.

## 2. Configure the Render Web Service
1. Sign in to [render.com](https://render.com) and choose **New ➔ Web Service**.
2. Connect your GitHub account and select this repository.
3. On the service setup screen:
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** leave blank and Render will read `Procfile` (`web: uvicorn main:app --host 0.0.0.0 --port $PORT`).
4. Choose an instance type (the free tier works for light usage) and create the service.

## 3. Environment Variables
In the Render service dashboard, add these environment variables under **Settings ➔ Environment**:
- `A2E_TOKEN`
- `DID_KEY`
- `HEYGEN_KEY`
- `PUBLIC_BASE_URL` → set to `https://your-service.onrender.com`

If you have a local `.env`, copy the same values. Render will restart automatically when you update them.

## 4. Deploy Updates
- Every time you push to the repository’s default branch, Render builds and deploys the backend automatically.
- Update `frontend/src/config.js` with the live Render URL so the local frontend hits the hosted backend.

## 5. Troubleshooting
- Check the **Logs** tab on Render if the build or deploy fails.
- Ensure `requirements.txt` contains all dependencies (FastAPI, Uvicorn, httpx, python-dotenv, etc.).
- Uploaded files live in `backend/uploads/`; they are git-ignored and should be handled by persistent storage if needed.

