# Vercel Setup - Quick Reference

## 📋 Pre-Deployment Checklist

- [ ] GitHub repository with code
- [ ] Google Gemini API key ([Get one](https://makersuite.google.com/app/apikey))
- [ ] Vercel account ([Sign up free](https://vercel.com/signup))

## 🚀 Deployment Steps

### 1. Import Project to Vercel

```
1. Go to vercel.com
2. Click "Add New..." → "Project"
3. Select "Import Git Repository"
4. Choose your GitHub repository
5. Vercel auto-detects configuration from vercel.json
```

### 2. Configure Environment Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

#### Required
```
GOOGLE_API_KEY=AIza...your-key-here
```

#### Optional (with defaults)
```
EMBEDDING_MODEL=all-MiniLM-L6-v2
RELEVANCE_THRESHOLD=0.5
TOP_K_CHUNKS=3
LLM_MODEL=gemini-1.5-flash
LLM_TEMPERATURE=0.3
```

**Important**: Set for all environments (Production, Preview, Development)

### 3. Deploy

```
1. Click "Deploy"
2. Wait 2-3 minutes
3. Visit your URL: https://your-app.vercel.app
```

## ✅ Post-Deployment Testing

### Test Questions

**Should Answer:**
```
"How do I create a new project in TaskFlow?"
"How do I add a team member?"
"What are the subscription plans?"
```

**Should Escalate:**
```
"What's the weather today?"
"Tell me a joke"
"How do I cook pasta?"
```

### Verify

- [ ] Frontend loads correctly
- [ ] Can submit questions
- [ ] Answers appear in chat
- [ ] Confidence explanations show
- [ ] Escalations work for out-of-scope questions

## 🔧 Common Issues

### Build Fails

**Error**: "Module not found"
```bash
# Solution: Ensure requirements.txt includes all dependencies
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### API Returns 500

**Error**: Function crashes
```bash
# Solution: Check Vercel function logs
1. Go to Vercel Dashboard → Deployments
2. Click on latest deployment
3. View Function Logs
4. Look for Python errors
```

### Frontend Can't Reach API

**Error**: "Failed to fetch"
```bash
# Solution: Test API directly
curl -X POST https://your-app.vercel.app/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"test"}'

# Should return JSON response
```

### Slow Responses

**Issue**: First request takes 5-10 seconds
```
This is normal! First request loads embedding model.
Subsequent requests are fast (1-3 seconds).
```

## 📊 Monitoring

### View Logs

```
Vercel Dashboard → Your Project → Deployments → Function Logs
```

### Key Metrics

- Function execution time: Should be <5s
- Error rate: Should be <5%
- Memory usage: Should be <1GB

### Enable Analytics

```
Vercel Dashboard → Analytics → Enable Web Analytics
```

## 🔄 Updating

### Update Code

```bash
git add .
git commit -m "Update feature"
git push
# Vercel auto-deploys
```

### Update Help Articles

```bash
vim data/articles/getting-started.md
git add data/articles/
git commit -m "Update help articles"
git push
# Vector store rebuilds automatically
```

### Update Environment Variables

```
1. Vercel Dashboard → Settings → Environment Variables
2. Edit variable
3. Redeploy (automatic or manual)
```

## 💰 Cost Tracking

### Free Tier Limits

- 100GB bandwidth/month
- 100 hours function execution/month
- 6,000 function invocations/day

### Monitor Usage

```
Vercel Dashboard → Usage
```

### Expected Usage (100-500 requests/day)

- Function time: ~1-2s per request
- Daily: 100-1000s = 0.03-0.3 hours
- Monthly: 1-9 hours
- **Well within free tier**

## 🆘 Getting Help

### Resources

- [Full Deployment Guide](DEPLOYMENT.md)
- [README](README.md)
- [Vercel Docs](https://vercel.com/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)

### Support Channels

1. Check function logs in Vercel Dashboard
2. Review [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
3. Open GitHub issue
4. Vercel support (Pro plan)

## 🎯 Next Steps

After successful deployment:

- [ ] Test with various questions
- [ ] Enable Vercel Analytics
- [ ] Set up custom domain (optional)
- [ ] Monitor performance
- [ ] Share with users!

---

**Quick Links:**
- [Vercel Dashboard](https://vercel.com/dashboard)
- [Google AI Studio](https://makersuite.google.com/app/apikey)
- [Full Documentation](DEPLOYMENT.md)
