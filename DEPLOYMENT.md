# Vercel Deployment Guide

This guide walks you through deploying the Smart Escalation API to Vercel as a monorepo with both frontend and backend.

## Quick Start

### 1. Prerequisites

- GitHub account with this repository
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Vercel account ([Sign up free](https://vercel.com/signup))

### 2. Deploy to Vercel

Click the button below to deploy:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/smart-escalation-api)

Or follow manual steps:

#### Step 1: Import Project

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Vercel will auto-detect the configuration from `vercel.json`

#### Step 2: Configure Environment Variables

Add these environment variables in the Vercel dashboard:

| Variable | Value | Required |
|----------|-------|----------|
| `GOOGLE_API_KEY` | Your Gemini API key | ✅ Yes |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | No (has default) |
| `RELEVANCE_THRESHOLD` | `0.5` | No (has default) |
| `TOP_K_CHUNKS` | `3` | No (has default) |
| `LLM_MODEL` | `gemini-1.5-flash` | No (has default) |
| `LLM_TEMPERATURE` | `0.3` | No (has default) |

**Important**: Set these for all environments (Production, Preview, Development)

#### Step 3: Deploy

1. Click "Deploy"
2. Wait 2-3 minutes for build
3. Visit your deployment URL

### 3. Test Your Deployment

1. Visit `https://your-app.vercel.app`
2. Try these test questions:
   - "How do I create a new project in TaskFlow?" (should answer)
   - "What's the weather today?" (should escalate)
3. Check that responses appear correctly

## Architecture

### Monorepo Structure

```
smart-escalation-api/
├── api/                    # Vercel Serverless Functions (Backend)
│   └── ask.py             # POST /api/ask endpoint
├── frontend/              # React Frontend
│   ├── src/
│   └── dist/              # Built static files
├── src/                   # Shared Python modules
│   ├── rag.py
│   ├── escalation.py
│   ├── llm_client.py
│   └── config.py
├── data/articles/         # Help articles knowledge base
├── vercel.json           # Vercel configuration
└── package.json          # Monorepo configuration
```

### How It Works

1. **Frontend**: React app built with Vite, served as static files
2. **Backend**: Python serverless function at `/api/ask`
3. **Same Origin**: Frontend calls `/api/ask` (no CORS needed)
4. **Automatic HTTPS**: Vercel provides SSL certificates
5. **Global CDN**: Fast access worldwide

## Configuration

### vercel.json

The `vercel.json` file configures:
- Python runtime for API functions
- Static build for frontend
- Routing rules (API vs frontend)

### Environment Variables

Set in Vercel Dashboard → Settings → Environment Variables

**Required:**
- `GOOGLE_API_KEY`: Your Gemini API key

**Optional (with defaults):**
- `EMBEDDING_MODEL`: Sentence transformer model
- `RELEVANCE_THRESHOLD`: Escalation threshold (0-1)
- `TOP_K_CHUNKS`: Number of chunks to retrieve
- `LLM_MODEL`: Gemini model to use
- `LLM_TEMPERATURE`: LLM temperature (0-1)

## Local Development

### Backend Only

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn src.main:app --reload
```

API available at: `http://localhost:8000`

### Frontend Only

```bash
# Install Node dependencies
cd frontend
npm install

# Set API URL for local backend
echo "VITE_API_URL=http://localhost:8000" > .env

# Run dev server
npm run dev
```

Frontend available at: `http://localhost:5173`

### Full Stack (Vercel Dev)

```bash
# Install Vercel CLI
npm install -g vercel

# Run local Vercel environment
vercel dev
```

This simulates the Vercel environment locally.

## Troubleshooting

### Build Fails

**Problem**: "Module not found" error

**Solution**:
- Ensure `requirements.txt` includes all dependencies
- Check Python version is 3.9+ in `vercel.json`
- Verify all files are committed to git

### API Returns 500

**Problem**: Serverless function crashes

**Solution**:
- Check function logs in Vercel Dashboard
- Verify `GOOGLE_API_KEY` is set correctly
- Ensure `data/articles/` directory exists
- Check that help articles are valid markdown

### Frontend Can't Reach API

**Problem**: "Failed to fetch" errors

**Solution**:
- Verify API endpoint: `https://your-app.vercel.app/api/ask`
- Check browser console for errors
- Test API directly with curl:
  ```bash
  curl -X POST https://your-app.vercel.app/api/ask \
    -H "Content-Type: application/json" \
    -d '{"question":"test"}'
  ```

### Slow Response Times

**Problem**: Requests take >10 seconds

**Solution**:
- First request loads embedding model (2-3s cold start)
- Subsequent requests are faster (cached)
- Use `gemini-1.5-flash` for faster responses
- Consider Vercel Pro for better performance

### Out of Memory

**Problem**: Function crashes with memory error

**Solution**:
- Vercel free tier: 1GB memory limit
- Reduce `TOP_K_CHUNKS` to use less memory
- Use smaller embedding model
- Upgrade to Pro plan for 3GB memory

## Monitoring

### Vercel Dashboard

Monitor your deployment:
1. Go to Vercel Dashboard → Your Project
2. View real-time logs in Deployments tab
3. Check function execution time and errors
4. Monitor bandwidth usage

### Enable Analytics

1. Go to Analytics tab in Vercel Dashboard
2. Enable Web Analytics (free)
3. Enable Speed Insights for performance monitoring

### Key Metrics

Watch for:
- Function execution time (should be <5s)
- Error rate (should be <5%)
- Cold start frequency
- Memory usage

## Updating

### Update Code

```bash
# Make changes
git add .
git commit -m "Update feature"
git push

# Vercel automatically deploys
```

### Update Help Articles

```bash
# Edit articles
vim data/articles/getting-started.md

# Commit and push
git add data/articles/
git commit -m "Update help articles"
git push

# Vercel redeploys, vector store rebuilds
```

### Update Dependencies

**Python:**
```bash
# Update requirements.txt
pip install new-package
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Add new dependency"
git push
```

**Node:**
```bash
cd frontend
npm install new-package
git add package.json package-lock.json
git commit -m "Add new dependency"
git push
```

## Cost Estimates

### Vercel Free Tier

- ✅ 100GB bandwidth/month
- ✅ 100 hours function execution/month
- ✅ 6,000 function invocations/day
- ✅ Unlimited deployments
- ✅ Automatic HTTPS
- ✅ Global CDN

### Expected Usage

For low-medium traffic (100-500 requests/day):
- Function time: ~1-2s per request
- Daily usage: 100-1000s = 0.03-0.3 hours/day
- Monthly usage: 1-9 hours/month
- **Well within free tier limits**

### When to Upgrade

Upgrade to Pro ($20/month) if you need:
- >100 hours function execution
- >6,000 requests/day
- 60s timeout (vs 10s)
- 3GB memory (vs 1GB)
- Priority support

### Additional Costs

- **Google Gemini API**: Free tier (15 req/min, 1500 req/day)
- **Total**: $0-20/month depending on traffic

## Security

### Best Practices

1. ✅ Never commit API keys to git
2. ✅ Use Vercel environment variables for secrets
3. ✅ Rotate API keys periodically
4. ✅ Monitor logs for suspicious activity
5. ✅ Keep dependencies updated

### Automatic Security

Vercel provides:
- ✅ Automatic HTTPS/SSL
- ✅ DDoS protection
- ✅ Secure environment variables
- ✅ Isolated function execution

## Support

### Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vercel Community](https://github.com/vercel/vercel/discussions)

### Getting Help

1. Check [README.md](README.md) for detailed documentation
2. Review [Troubleshooting](#troubleshooting) section above
3. Check Vercel function logs for errors
4. Open GitHub issue for bugs
5. Contact Vercel support (Pro plan)

## Next Steps

After deployment:

1. ✅ Test with various questions
2. ✅ Monitor performance in Vercel Dashboard
3. ✅ Enable Analytics for insights
4. ✅ Set up custom domain (optional)
5. ✅ Configure alerts for errors
6. ✅ Share with users!

---

**Need help?** Open an issue on GitHub or check the [README.md](README.md) for more details.
