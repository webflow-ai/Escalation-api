# Smart Escalation API

An AI-powered L1 customer support system that intelligently answers customer questions about TaskFlow (a fictional project management SaaS) or escalates to human agents when uncertain. The system uses RAG-based retrieval over help articles to ground responses.

## 🚀 Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

1. Click the button above or go to [vercel.com](https://vercel.com)
2. Import this repository
3. Add environment variable: `GOOGLE_API_KEY` (get from [Google AI Studio](https://makersuite.google.com/app/apikey))
4. Deploy!

**See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.**

## Features

- **RAG-Based Retrieval**: Uses sentence-transformers and FAISS for semantic search over help articles
- **Intelligent Escalation**: Automatically escalates to human agents when confidence is low
- **FastAPI Backend**: Fast, async API with automatic OpenAPI documentation
- **React Chat UI**: Minimal, functional chat interface for customer interaction
- **Free Hosting Compatible**: No external databases required, deployable to free tiers

## Architecture

- **Backend**: Python serverless functions on Vercel
- **Vector Store**: FAISS (in-memory) with sentence-transformers embeddings
- **LLM**: Google Gemini API (gemini-1.5-flash)
- **Frontend**: React + Vite + TypeScript
- **Deployment**: Vercel (monorepo with frontend + backend)

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend)
- Google Gemini API key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-escalation-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

5. **Run the server**
   ```bash
   uvicorn src.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and set VITE_API_URL to your backend URL
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

   The UI will be available at `http://localhost:5173`

## Project Structure

```
smart-escalation-api/
├── data/
│   └── articles/          # Help article knowledge base (markdown files)
├── src/
│   ├── main.py           # FastAPI application
│   ├── rag.py            # RAG system with FAISS vector store
│   ├── escalation.py     # Escalation decision engine
│   ├── llm_client.py     # LLM API client (Google Gemini)
│   ├── chunking.py       # Text chunking logic
│   └── config.py         # Configuration management
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── property/         # Property-based tests (Hypothesis)
├── frontend/
│   └── src/              # React chat interface
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
└── README.md            # This file
```

## API Usage

### POST /ask

Submit a customer question and receive an answer or escalation.

**Request:**
```json
{
  "question": "How do I add a team member to my project?"
}
```

**Response (Answer):**
```json
{
  "response_type": "answer",
  "message": "To add a team member to your project in TaskFlow, go to Project Settings > Team Members and click 'Invite Member'. You can set their role as Viewer, Editor, or Admin.",
  "confidence_explanation": "High confidence - retrieved relevant content from 'Managing Team Permissions' article with similarity score 0.82",
  "sources": ["permissions.md"]
}
```

**Response (Escalation):**
```json
{
  "response_type": "escalation",
  "message": "I'm not certain I can answer this accurately. Let me connect you with a human support agent who can help.",
  "confidence_explanation": "Low confidence - best retrieval score was 0.42, indicating question may be outside help article scope",
  "sources": null
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key (required) | - |
| `EMBEDDING_MODEL` | Sentence-transformers model name | `all-MiniLM-L6-v2` |
| `RELEVANCE_THRESHOLD` | Minimum similarity score to answer (0-1) | `0.5` |
| `TOP_K_CHUNKS` | Number of chunks to retrieve | `3` |
| `CHUNK_SIZE` | Characters per chunk | `500` |
| `CHUNK_OVERLAP` | Overlap between chunks | `50` |
| `LLM_MODEL` | LLM model name | `gemini-1.5-flash` |
| `LLM_TEMPERATURE` | LLM temperature (0-1) | `0.3` |

### Escalation Logic

The system escalates to human agents when:
- Best chunk relevance score < `RELEVANCE_THRESHOLD` (default 0.5)
- LLM signals uncertainty in its response
- No relevant chunks are retrieved

## Deployment

This section provides step-by-step instructions for deploying the entire Smart Escalation API (both backend and frontend) to Vercel.

### Why Vercel for Everything?

Vercel supports both:
- **Frontend**: Static React apps (traditional use case)
- **Backend**: Python serverless functions via API routes

This means you can deploy the entire application to a single platform with:
- ✅ Single deployment workflow
- ✅ Unified environment variables
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Free tier for both frontend and backend

### Prerequisites

- GitHub account with your repository
- Google Gemini API key
- Vercel account (free tier available at [vercel.com](https://vercel.com))

### Project Structure for Vercel

First, we need to restructure the project to work with Vercel's serverless functions:

```
smart-escalation-api/
├── api/                    # Backend API (Vercel Serverless Functions)
│   └── ask.py             # POST /api/ask endpoint
├── frontend/              # React frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── src/                   # Shared Python modules
│   ├── rag.py
│   ├── escalation.py
│   ├── llm_client.py
│   ├── chunking.py
│   └── config.py
├── data/
│   └── articles/          # Help articles
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
└── package.json          # Root package.json for monorepo
```

### Step 1: Create Vercel Configuration

Create `vercel.json` in the project root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.py",
      "use": "@vercel/python"
    },
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "frontend/dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.9"
  }
}
```

### Step 2: Create API Endpoint

Create `api/ask.py` to handle the `/api/ask` endpoint:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
import os

# Add parent directory to path to import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag import RAGSystem
from src.escalation import EscalationEngine
from src.llm_client import LLMClient
from src.config import Settings

# Initialize components (cached across invocations)
settings = Settings()
rag_system = RAGSystem(articles_dir="data/articles")
llm_client = LLMClient(api_key=settings.google_api_key)
escalation_engine = EscalationEngine(llm_client=llm_client)

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.post("/api/ask")
async def ask_question(request: QuestionRequest):
    """Process customer question and return answer or escalation."""
    try:
        # Retrieve relevant chunks
        chunks = rag_system.retrieve(request.question, top_k=settings.top_k_chunks)
        
        # Decide whether to answer or escalate
        decision = escalation_engine.process_question(request.question, chunks)
        
        return JSONResponse(content={
            "response_type": decision.action,
            "message": decision.message,
            "confidence_explanation": decision.confidence_explanation,
            "sources": decision.sources
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "response_type": "escalation",
                "message": "I'm experiencing technical difficulties. Let me connect you with a human agent.",
                "confidence_explanation": f"Error: {str(e)}",
                "sources": None
            }
        )

# Vercel serverless function handler
async def handler(request: Request):
    return await app(request)
```

### Step 3: Update Frontend API URL

Update `frontend/src/services/api.ts` to use relative API path:

```typescript
const API_URL = import.meta.env.VITE_API_URL || '/api';

export async function askQuestion(question: string) {
  const response = await fetch(`${API_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to get response');
  }
  
  return response.json();
}
```

### Step 4: Deploy to Vercel

#### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Create a Vercel Account**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with your GitHub account

2. **Import Project**
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Vercel will auto-detect the configuration

3. **Configure Environment Variables**
   
   In the "Environment Variables" section, add:
   
   | Variable | Value | Notes |
   |----------|-------|-------|
   | `GOOGLE_API_KEY` | `AIza...` | **Required** - Your Gemini API key |
   | `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Optional - defaults to this |
   | `RELEVANCE_THRESHOLD` | `0.5` | Optional - adjust escalation sensitivity |
   | `TOP_K_CHUNKS` | `3` | Optional - number of chunks to retrieve |
   | `LLM_MODEL` | `gemini-1.5-flash` | Optional - use flash for speed |
   | `LLM_TEMPERATURE` | `0.3` | Optional - lower = more deterministic |
   
   **Important**: Set these for all environments (Production, Preview, Development)

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for build and deployment
   - Monitor build logs for any errors

5. **Verify Deployment**
   - Visit your Vercel URL (e.g., `https://smart-escalation-api.vercel.app`)
   - Test the chat interface
   - Submit a test question
   - Check browser console for any errors

#### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```
   
   Follow the prompts:
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N**
   - Project name? `smart-escalation-api`
   - In which directory is your code located? `./`

4. **Add Environment Variables**
   ```bash
   vercel env add GOOGLE_API_KEY
   vercel env add EMBEDDING_MODEL
   vercel env add RELEVANCE_THRESHOLD
   # ... add other variables
   ```

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

### Step 5: Configure Custom Domain (Optional)

1. Go to your project in Vercel Dashboard
2. Navigate to Settings → Domains
3. Add your custom domain (e.g., `support.yourdomain.com`)
4. Follow DNS configuration instructions:
   - Add CNAME record pointing to `cname.vercel-dns.com`
   - Or add A record pointing to Vercel's IP
5. Wait for DNS propagation (5-30 minutes)
6. Vercel automatically provisions SSL certificate

### Deployment Troubleshooting

#### Vercel Serverless Function Issues

**Problem: "Module not found" in API functions**
- **Solution**: Ensure `requirements.txt` is in project root
- Verify Python version is 3.9+ in `vercel.json`
- Check that `src/` modules are importable from `api/` directory
- Add `sys.path.append()` in `api/ask.py` if needed

**Problem: API function times out (10 second limit)**
- **Solution**: Vercel serverless functions have 10s timeout on free tier
- Optimize embedding model loading (cache between invocations)
- Consider upgrading to Pro plan for 60s timeout
- Use lighter embedding model if needed

**Problem: "Function size exceeds limit"**
- **Solution**: Vercel has 250MB limit for serverless functions
- Reduce dependencies in `requirements.txt`
- Use `.vercelignore` to exclude unnecessary files:
  ```
  tests/
  .pytest_cache/
  .hypothesis/
  *.pyc
  __pycache__/
  ```

**Problem: Cold start takes too long**
- **Solution**: First request after inactivity loads embedding model (~2-3s)
- This is normal for serverless architecture
- Subsequent requests are fast (cached)
- Consider keeping function warm with periodic pings

**Problem: Environment variables not accessible**
- **Solution**: Ensure variables are set in Vercel dashboard
- Redeploy after adding new environment variables
- Check variable names match exactly (case-sensitive)
- Verify variables are set for correct environment (Production/Preview)

#### Frontend Issues

**Problem: Build fails with "Cannot find module"**
- **Solution**: Ensure `frontend/package.json` includes all dependencies
- Verify Node.js version (requires 18+)
- Run `npm install` locally to test
- Check `frontend/` is set as root directory in build settings

**Problem: Frontend loads but API calls fail with 404**
- **Solution**: Verify API routes are configured in `vercel.json`
- Check that `api/ask.py` exists and is properly structured
- Test API endpoint directly: `https://your-app.vercel.app/api/ask`
- Ensure frontend is calling `/api/ask` (not `/ask`)

**Problem: CORS errors in browser console**
- **Solution**: With Vercel monorepo, CORS shouldn't be needed (same origin)
- If using separate deployments, add CORS headers to API function
- Verify frontend and API are on same domain

**Problem: "Failed to fetch" errors**
- **Solution**: Check browser console for detailed error
- Verify API endpoint is accessible
- Test with curl: `curl -X POST https://your-app.vercel.app/api/ask -H "Content-Type: application/json" -d '{"question":"test"}'`
- Check network tab in browser dev tools

#### Build and Deployment Issues

**Problem: Build fails with Python errors**
- **Solution**: Check build logs in Vercel dashboard
- Verify all Python dependencies are in `requirements.txt`
- Ensure Python version compatibility (3.9+)
- Test locally: `pip install -r requirements.txt`

**Problem: Build succeeds but deployment fails**
- **Solution**: Check deployment logs for runtime errors
- Verify `vercel.json` configuration is correct
- Ensure all required files are committed to git
- Check that `data/articles/` directory exists with help articles

**Problem: Changes not reflecting after deployment**
- **Solution**: Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check that git changes are committed and pushed
- Verify Vercel deployed the correct branch
- Check deployment logs to confirm new version deployed

**Problem: Preview deployments work but production fails**
- **Solution**: Check environment variables are set for Production
- Verify production branch is correct (usually `main`)
- Compare environment variables between Preview and Production
- Check for hardcoded URLs or environment-specific code

#### Performance Issues

**Problem: Slow response times (>10 seconds)**
- **Solution**: Vercel free tier has 10s timeout for serverless functions
- Check LLM API latency in function logs
- Use `gemini-1.5-flash` instead of `gemini-1.5-pro`
- Optimize embedding model loading
- Consider upgrading to Pro plan for better performance

**Problem: Out of memory errors**
- **Solution**: Vercel serverless functions have 1GB memory limit (free tier)
- Reduce `TOP_K_CHUNKS` to decrease memory usage
- Use smaller embedding model
- Optimize chunk storage and retrieval
- Upgrade to Pro plan for 3GB memory

**Problem: Rate limiting from Vercel**
- **Solution**: Free tier has limits on function invocations
- Monitor usage in Vercel dashboard
- Implement client-side rate limiting
- Upgrade to Pro plan for higher limits

#### API Key and Authentication Issues

**Problem: "Invalid API key" errors**
- **Solution**: Verify `GOOGLE_API_KEY` is set correctly in Vercel
- Check API key has proper permissions
- Ensure quota is not exceeded
- Test API key with direct Gemini API call

**Problem: API key works locally but not on Vercel**
- **Solution**: Ensure environment variable is set in Vercel dashboard
- Redeploy after adding environment variables
- Check variable name matches exactly (case-sensitive)
- Verify no extra spaces or quotes in variable value

#### Data and File Issues

**Problem: Help articles not found**
- **Solution**: Ensure `data/articles/` directory is committed to git
- Verify file paths are correct (case-sensitive)
- Check that markdown files exist and are readable
- Test locally first: `ls data/articles/`

**Problem: Vector store fails to build**
- **Solution**: Check that all help articles are valid markdown
- Verify embedding model downloads successfully
- Check function logs for specific error messages
- Ensure sufficient memory for vector store creation

### Monitoring and Maintenance

#### Vercel Analytics

Enable Vercel Analytics to monitor:
- Page views and user traffic
- API function invocations
- Response times and errors
- Bandwidth usage

**To enable:**
1. Go to your project in Vercel Dashboard
2. Navigate to Analytics tab
3. Enable Web Analytics (free)
4. Enable Speed Insights for performance monitoring

#### Function Logs

Monitor serverless function logs:
1. Go to Vercel Dashboard → Your Project
2. Click on Deployments → Select deployment
3. View Function Logs for real-time monitoring
4. Check for errors, warnings, and performance metrics

**Key metrics to watch:**
- Function execution time (should be <5s)
- Error rate (should be <5%)
- Cold start frequency
- Memory usage

#### Updating the Application

**To update help articles:**
1. Edit markdown files in `data/articles/`
2. Commit and push to GitHub
3. Vercel automatically redeploys
4. Vector store rebuilds on next function invocation

**To update code:**
1. Make changes to Python or React code
2. Test locally first
3. Commit and push to GitHub
4. Vercel automatically builds and deploys
5. Monitor deployment logs for errors

**To update dependencies:**
1. Update `requirements.txt` (Python) or `package.json` (Node)
2. Test locally: `pip install -r requirements.txt` or `npm install`
3. Commit and push
4. Vercel rebuilds with new dependencies

### Cost Estimates

**Vercel Free Tier Limits:**
- 100GB bandwidth per month
- 100 hours serverless function execution per month
- 6,000 function invocations per day
- 1GB function memory
- 10s function timeout
- Unlimited deployments

**Expected Usage for Low-Medium Traffic:**
- ~1-2s per API request
- ~100-500 requests/day = 100-500s function time/day
- ~3,000-15,000s function time/month = 0.8-4.2 hours/month
- Well within free tier limits

**When to Upgrade to Pro ($20/month):**
- Need >100 hours function execution
- Need >6,000 requests/day
- Need 60s timeout (vs 10s)
- Need 3GB memory (vs 1GB)
- Need priority support

**Additional Costs:**
- **Google Gemini API**: $0-10/month (free tier: 15 req/min, 1500 req/day)
- **Total**: $0-30/month depending on traffic

### Security Best Practices

1. **Environment Variables**
   - Never commit API keys to git
   - Use Vercel environment variables for all secrets
   - Rotate API keys periodically

2. **CORS Configuration**
   - With Vercel monorepo, CORS is handled automatically (same origin)
   - If using separate deployments, restrict CORS to specific domains

3. **Input Validation**
   - Already handled by Pydantic models
   - Limit question length (max 500 characters)
   - Sanitize user input

4. **Rate Limiting**
   - Implement client-side throttling
   - Consider adding server-side rate limiting for production
   - Monitor for abuse in Vercel logs

5. **HTTPS**
   - Vercel provides automatic HTTPS
   - All traffic is encrypted by default
   - SSL certificates auto-renewed

6. **Monitoring**
   - Enable Vercel Analytics
   - Monitor function logs regularly
   - Set up alerts for errors or unusual traffic

### Advanced Configuration

#### Custom Build Configuration

Create `package.json` in project root for monorepo setup:

```json
{
  "name": "smart-escalation-api",
  "version": "1.0.0",
  "scripts": {
    "build": "cd frontend && npm install && npm run build"
  },
  "workspaces": [
    "frontend"
  ]
}
```

#### Optimizing Cold Starts

Add warming function to keep serverless functions active:

```python
# api/health.py
def handler(request):
    return {
        "statusCode": 200,
        "body": {"status": "healthy"}
    }
```

Set up external monitoring (e.g., UptimeRobot) to ping `/api/health` every 5 minutes.

#### Environment-Specific Configuration

Use Vercel's environment system:
- **Production**: Live environment with production API keys
- **Preview**: Staging environment for testing (auto-created for PRs)
- **Development**: Local development environment

Set different values for each environment in Vercel dashboard.

### Getting Help

**Vercel Support:**
- Documentation: [vercel.com/docs](https://vercel.com/docs)
- Community: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- Support: Available for Pro plan users

**Common Resources:**
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
- [Vercel Monorepo Guide](https://vercel.com/docs/monorepos)

## Testing

### Run Unit Tests
```bash
pytest tests/unit -v
```

### Run Property-Based Tests
```bash
pytest tests/property -v
```

### Run Integration Tests
```bash
pytest tests/integration -v
```

### Run All Tests
```bash
pytest -v
```

## Help Articles

The system includes 5 help articles about TaskFlow:

1. **Getting Started** - TaskFlow basics, account setup, first project
2. **Billing and Subscriptions** - Plans, payment methods, billing cycles
3. **Integrations** - Slack, GitHub, Jira integrations
4. **Team Permissions** - Roles, access control, admin settings
5. **Troubleshooting** - Common errors, login issues, performance tips

Articles are stored as markdown files in `data/articles/`.

## Development

### Adding New Help Articles

1. Create a new markdown file in `data/articles/`
2. Restart the server to rebuild the vector store
3. Test retrieval with relevant questions

### Adjusting Escalation Threshold

Edit `RELEVANCE_THRESHOLD` in `.env`:
- Lower values (e.g., 0.3): Answer more questions, risk lower quality
- Higher values (e.g., 0.7): Escalate more often, ensure high quality

### Switching LLM Models

**Gemini Flash (faster, cheaper):**
```bash
GOOGLE_API_KEY=AIza...
LLM_MODEL=gemini-1.5-flash
```

**Gemini Pro (more capable):**
```bash
GOOGLE_API_KEY=AIza...
LLM_MODEL=gemini-1.5-pro
```

## Troubleshooting

### "Module not found" errors
```bash
# Ensure you're in the virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### "API key not found" errors
```bash
# Check .env file exists and contains valid API key
cat .env
```

### Slow first request
The first request loads the embedding model (~100MB), which takes 2-3 seconds. Subsequent requests are fast.

### CORS errors in frontend
Ensure `VITE_API_URL` in frontend `.env` matches your backend URL exactly (no trailing slash).

## Performance

- **Startup time**: 2-3 seconds (loading articles and embedding model)
- **Response time**: 3-5 seconds (95th percentile)
  - Embedding generation: ~100ms
  - Vector search: ~50ms
  - LLM API call: 2-4 seconds
- **Memory usage**: ~150MB (embedding model + FAISS index)

## License

MIT

## Support

For questions or issues, please open a GitHub issue or contact the development team.
