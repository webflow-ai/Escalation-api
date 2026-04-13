# Smart Escalation API - Deployment Options

## ⚠️ Critical Constraint

Your application uses heavy ML dependencies (~5GB total):
- `sentence-transformers` (~2GB with PyTorch)
- `faiss-cpu` (~500MB)
- `torch` (~2GB)
- CUDA libraries and other dependencies

**Vercel serverless functions have a 500MB size limit** - your dependencies are 10x larger.

## Option 1: Hybrid Deployment (RECOMMENDED)

Deploy frontend and backend separately:

### Frontend → Vercel
- ✅ Already working at `https://escalation-api-frontend.vercel.app/`
- Static React app (no size limits)
- Fast global CDN

### Backend → Render/Railway/Hugging Face
- Deploy the full Python ML backend
- No size limits
- Persistent containers (not serverless)

**Steps:**
1. Deploy backend to Render (see `BACKEND_DEPLOY.md`)
2. Get backend URL (e.g., `https://your-app.onrender.com`)
3. Add `VITE_API_URL` environment variable in Vercel
4. Redeploy frontend

**Cost:** 
- Vercel: Free
- Render: $7/month (Starter plan)
- Total: $7/month

---

## Option 2: API Gateway Pattern (Vercel Frontend + Proxy)

Keep everything "on Vercel" by using a lightweight proxy:

### Architecture
```
User → Vercel Frontend → Vercel Proxy (api/proxy.py) → External ML Backend
```

### What's on Vercel
- Frontend (static React)
- Lightweight Python proxy (no ML dependencies, <1MB)

### What's External
- Full ML backend on Render/Railway/Hugging Face

**Steps:**
1. Deploy ML backend to Render
2. Update `vercel.json` to use `api/proxy.py`
3. Set `ML_BACKEND_URL` environment variable in Vercel
4. Deploy to Vercel

**Benefit:** Everything appears to be "on Vercel" from user perspective

---

## Option 3: Full Vercel (NOT POSSIBLE)

❌ Cannot deploy ML dependencies to Vercel serverless functions
❌ 500MB limit vs 5GB dependencies
❌ Multiple attempts failed with size errors

**Why it fails:**
```
Error: Total dependency size (4995.65 MB) exceeds Lambda 
ephemeral storage limit (500 MB)
```

---

## Recommended Solution: Option 1 (Hybrid)

This is the standard approach for ML applications:

### 1. Deploy Backend to Render

```bash
# Create render.yaml
cat > render.yaml << 'EOF'
services:
  - type: web
    name: escalation-api-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GOOGLE_API_KEY
        sync: false
      - key: ARTICLES_DIR
        value: data/articles
      - key: EMBEDDING_MODEL
        value: all-MiniLM-L6-v2
      - key: RELEVANCE_THRESHOLD
        value: "0.5"
      - key: TOP_K_CHUNKS
        value: "3"
      - key: CHUNK_SIZE
        value: "500"
      - key: CHUNK_OVERLAP
        value: "50"
      - key: LLM_MODEL
        value: gemini-1.5-flash
      - key: LLM_TEMPERATURE
        value: "0.3"
      - key: CORS_ORIGINS
        value: https://escalation-api-frontend.vercel.app
EOF

# Add FastAPI and uvicorn to requirements.txt
echo "fastapi==0.104.1" >> requirements.txt
echo "uvicorn[standard]==0.24.0" >> requirements.txt

# Commit and push
git add .
git commit -m "Add Render deployment config"
git push

# Deploy on Render dashboard
# 1. Go to https://dashboard.render.com
# 2. New → Web Service
# 3. Connect your GitHub repo
# 4. Render will auto-detect render.yaml
# 5. Add GOOGLE_API_KEY in environment variables
# 6. Deploy
```

### 2. Connect Frontend to Backend

```bash
# In Vercel dashboard:
# 1. Go to your project settings
# 2. Environment Variables
# 3. Add: VITE_API_URL = https://your-app.onrender.com
# 4. Redeploy frontend
```

### 3. Test End-to-End

```bash
# Test backend directly
curl -X POST https://your-app.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?"}'

# Test frontend
# Visit https://escalation-api-frontend.vercel.app/
# Ask a question
```

---

## Why Not Vercel for ML?

Vercel is optimized for:
- ✅ Static sites (Next.js, React, Vue)
- ✅ Lightweight serverless functions (<50MB)
- ✅ Edge functions (<1MB)

Vercel is NOT suitable for:
- ❌ Heavy ML models (>500MB)
- ❌ Long-running processes (>10s timeout)
- ❌ GPU workloads
- ❌ Large binary dependencies

For ML applications, use:
- Render (persistent containers)
- Railway (persistent containers)
- Hugging Face Spaces (ML-optimized)
- AWS Lambda with container images (10GB limit)
- Google Cloud Run (ML-optimized)

---

## Next Steps

Choose your deployment strategy:

**Option 1 (Recommended):** Follow the Render deployment steps above

**Option 2 (API Gateway):** Use `api/proxy.py` and deploy ML backend separately

**Need help?** Check `BACKEND_DEPLOY.md` for detailed Render instructions.
