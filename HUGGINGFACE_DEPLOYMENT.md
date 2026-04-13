# 🤗 Deploy to Hugging Face Spaces (FREE)

Complete step-by-step guide to deploy your Smart Escalation API to Hugging Face Spaces for FREE.

## Why Hugging Face Spaces?

- ✅ **FREE** - No credit card required
- ✅ **2GB RAM** - Enough for ML models (vs Render's 512MB free tier)
- ✅ **Optimized for ML** - Built for apps like yours
- ✅ **Easy deployment** - Push code via Git
- ✅ **Automatic HTTPS** - Secure by default

---

## Step 1: Create Hugging Face Account (2 minutes)

1. **Go to Hugging Face**
   - Visit: https://huggingface.co/join

2. **Sign Up**
   - Enter your email
   - Choose a username (e.g., `yourname`)
   - Create password
   - Verify email

3. **Get Access Token**
   - Go to: https://huggingface.co/settings/tokens
   - Click **"New token"**
   - Name: `escalation-api-deploy`
   - Role: **Write**
   - Click **"Generate a token"**
   - **Copy the token** - you'll need it soon!

---

## Step 2: Create a New Space (3 minutes)

1. **Create Space**
   - Go to: https://huggingface.co/new-space
   - Or click your profile → **"New Space"**

2. **Configure Space**
   - **Owner**: Your username
   - **Space name**: `escalation-api` (or any name you like)
   - **License**: MIT
   - **Select the Space SDK**: Choose **"Docker"** (important!)
   - **Space hardware**: CPU basic (free)
   - **Visibility**: Public
   - Click **"Create Space"**

3. **Wait for Space Creation**
   - You'll see a page with instructions
   - Keep this page open

---

## Step 3: Add Required Files (5 minutes)

We need to add a few files for Hugging Face Spaces:

### 3.1: Create Dockerfile

I'll create a Dockerfile for you:

```bash
# This will be created automatically in the next step
```

### 3.2: Create .env.example for Spaces

```bash
# This will be created automatically in the next step
```

Let me create these files now:

---

## Step 4: Push Code to Hugging Face (5 minutes)

### 4.1: Add Hugging Face Remote

Open your terminal and run:

```bash
# Add Hugging Face as a git remote
# Replace YOUR_USERNAME with your actual Hugging Face username
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/escalation-api
```

Example:
```bash
git remote add hf https://huggingface.co/spaces/john/escalation-api
```

### 4.2: Commit New Files

```bash
# Add the new Hugging Face files
git add Dockerfile README_SPACES.md app.py

# Commit
git commit -m "Add Hugging Face Spaces deployment files"
```

### 4.3: Push to Hugging Face

```bash
# Push to Hugging Face Spaces
git push hf main
```

**You'll be prompted for credentials:**
- **Username**: Your Hugging Face username
- **Password**: Use the **access token** you created in Step 1 (NOT your password!)

---

## Step 5: Configure Environment Variables (3 minutes)

1. **Go to Your Space**
   - Visit: `https://huggingface.co/spaces/YOUR_USERNAME/escalation-api`

2. **Open Settings**
   - Click the **"Settings"** tab at the top

3. **Add Secrets (Environment Variables)**
   - Scroll down to **"Repository secrets"**
   - Click **"New secret"** for each variable:

   | Name | Value |
   |------|-------|
   | `GOOGLE_API_KEY` | Your Gemini API key from https://makersuite.google.com/app/apikey |
   | `ARTICLES_DIR` | `data/articles` |
   | `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` |
   | `RELEVANCE_THRESHOLD` | `0.5` |
   | `TOP_K_CHUNKS` | `3` |
   | `CHUNK_SIZE` | `500` |
   | `CHUNK_OVERLAP` | `50` |
   | `LLM_MODEL` | `gemini-1.5-flash` |
   | `LLM_TEMPERATURE` | `0.3` |
   | `CORS_ORIGINS` | `https://escalation-api-frontend.vercel.app,http://localhost:5173` |

4. **Save Each Secret**
   - Click **"Add secret"** after entering each one

---

## Step 6: Wait for Build (10-15 minutes)

1. **Go to "App" Tab**
   - Click the **"App"** tab at the top

2. **Watch Build Logs**
   - You'll see the Docker build progress
   - It will download ML models (~2GB)
   - This takes 10-15 minutes on first build

3. **Build Complete**
   - When done, you'll see: **"Running"** status
   - Your API is now live! 🎉

---

## Step 7: Test Your API (2 minutes)

### 7.1: Get Your API URL

Your API is available at:
```
https://YOUR_USERNAME-escalation-api.hf.space
```

Example:
```
https://john-escalation-api.hf.space
```

### 7.2: Test with curl

```bash
curl -X POST https://YOUR_USERNAME-escalation-api.hf.space/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?"}'
```

### 7.3: Test in Browser

Visit:
```
https://YOUR_USERNAME-escalation-api.hf.space/docs
```

You'll see interactive API documentation where you can test the `/ask` endpoint.

---

## Step 8: Connect Frontend to Backend (5 minutes)

Now connect your Vercel frontend to the Hugging Face backend:

### 8.1: Copy Your Backend URL

```
https://YOUR_USERNAME-escalation-api.hf.space
```

### 8.2: Add to Vercel

1. Go to https://vercel.com/dashboard
2. Open your project: `escalation-api-frontend`
3. Go to **Settings** → **Environment Variables**
4. Click **"Add New"**
   - **Key**: `VITE_API_URL`
   - **Value**: `https://YOUR_USERNAME-escalation-api.hf.space`
   - **Environments**: Check all (Production, Preview, Development)
5. Click **"Save"**

### 8.3: Redeploy Frontend

1. Go to **Deployments** tab
2. Find the latest deployment
3. Click **"⋯"** (three dots) → **"Redeploy"**
4. Click **"Redeploy"** to confirm
5. Wait 1-2 minutes

---

## Step 9: Test End-to-End (1 minute)

1. **Visit Your Frontend**
   - Go to: https://escalation-api-frontend.vercel.app/

2. **Ask a Question**
   - Type: "How do I reset my password?"
   - Click **"Send"**

3. **Success!** 🎉
   - You should get an answer from your Hugging Face backend
   - Your full-stack ML app is now live!

---

## 🎉 Deployment Complete!

Your app is now fully deployed:

- **Frontend**: https://escalation-api-frontend.vercel.app/ (Vercel - FREE)
- **Backend**: https://YOUR_USERNAME-escalation-api.hf.space (Hugging Face - FREE)
- **Total Cost**: $0/month 🎊

---

## Troubleshooting

### Build fails with "Out of memory"

**Solution**: Upgrade to Hugging Face Pro ($9/month) for more resources, or:
- Use a smaller embedding model: `all-MiniLM-L6-v2` → `paraphrase-MiniLM-L3-v2`
- Reduce dependencies in `requirements.txt`

### "Application startup failed"

**Solution**: Check the logs in the "App" tab:
- Verify `GOOGLE_API_KEY` is set correctly
- Check that all environment variables are set
- Look for Python errors in the logs

### API returns 404

**Solution**: 
- Make sure the Space is "Running" (not "Building" or "Sleeping")
- Check the URL is correct: `https://YOUR_USERNAME-escalation-api.hf.space`
- Visit `/docs` to see available endpoints

### Frontend shows "Failed to fetch"

**Solution**:
- Verify `VITE_API_URL` is set in Vercel
- Check backend URL is correct (no trailing slash)
- Make sure Hugging Face Space is running
- Check CORS_ORIGINS includes your Vercel frontend URL

### Space goes to sleep

**Solution**: Hugging Face Spaces on free tier sleep after inactivity:
- First request after sleep takes 30-60 seconds (cold start)
- Subsequent requests are fast
- Upgrade to Pro ($9/month) for always-on instances

---

## Updating Your App

To update your code:

```bash
# Make changes to your code
git add .
git commit -m "Update feature"

# Push to GitHub (for version control)
git push origin main

# Push to Hugging Face (to deploy)
git push hf main
```

Hugging Face will automatically rebuild and redeploy.

---

## Cost Comparison

| Platform | Free Tier | Paid Tier | RAM | Notes |
|----------|-----------|-----------|-----|-------|
| **Hugging Face** | FREE | $9/month | 2GB | Best for ML apps |
| **Render** | 512MB (too small) | $7/month | 512MB+ | Good for web apps |
| **Railway** | $5 credit | $5-20/month | 512MB+ | Pay as you go |
| **Vercel** | ❌ Can't deploy ML | ❌ Can't deploy ML | 500MB limit | Frontend only |

---

## Next Steps

- ✅ Your app is live and working!
- 📊 Monitor usage in Hugging Face dashboard
- 🔧 Add more help articles in `data/articles/`
- 🎨 Customize the frontend
- 📈 Track API usage and performance

---

## Need Help?

- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **Hugging Face Discord**: https://discord.gg/hugging-face
- **Your Space Settings**: https://huggingface.co/spaces/YOUR_USERNAME/escalation-api/settings

Enjoy your FREE ML-powered API! 🚀
