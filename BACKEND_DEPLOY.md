# Backend Deployment Guide

The backend cannot be deployed to Vercel due to Python dependency issues (faiss-cpu compatibility).

## Option 1: Deploy Backend to Render (Recommended)

1. Go to [render.com](https://render.com) and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `escalation-api-backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `GOOGLE_API_KEY`: Your Gemini API key
6. Deploy

Your backend will be at: `https://escalation-api-backend.onrender.com`

## Option 2: Deploy Backend to Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables in the Variables tab
5. Railway auto-deploys

Your backend will be at: `https://your-app.up.railway.app`

## Update Frontend

After deploying the backend, update the frontend environment variable in Vercel:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add/Update: `VITE_API_URL` = `https://your-backend-url.onrender.com`
3. Redeploy frontend

## Local Development

### Backend:
```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL=http://localhost:8000` in `frontend/.env`
