# Smart Escalation API

An AI-powered L1 customer support system that intelligently answers customer questions about TaskFlow (a fictional project management SaaS) or escalates to human agents when uncertain. The system uses RAG-based retrieval over help articles to ground responses.

## Features

- **RAG-Based Retrieval**: Uses sentence-transformers and FAISS for semantic search over help articles
- **Intelligent Escalation**: Automatically escalates to human agents when confidence is low
- **FastAPI Backend**: Fast, async API with automatic OpenAPI documentation
- **React Chat UI**: Minimal, functional chat interface for customer interaction
- **Free Hosting Compatible**: No external databases required, deployable to free tiers

## Architecture

- **Backend**: FastAPI + FAISS (in-memory vector store) + sentence-transformers
- **LLM**: Google Gemini API (gemini-1.5-flash)
- **Frontend**: React + Vite + TypeScript
- **Deployment**: Render/Railway (backend) + Vercel (frontend)

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

### Backend Deployment (Render/Railway)

#### Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure build settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `GOOGLE_API_KEY`
   - Other configuration variables as needed
5. Deploy

#### Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables in the Variables tab
4. Railway will auto-detect Python and deploy
5. Set start command if needed: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel)

1. Create a new project on [Vercel](https://vercel.com)
2. Connect your GitHub repository
3. Configure build settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add environment variable:
   - `VITE_API_URL`: Your backend URL (e.g., `https://your-app.onrender.com`)
5. Deploy

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
