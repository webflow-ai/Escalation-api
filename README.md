---
title: Smart Escalation API
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

# Smart Escalation API

AI-powered L1 customer support system that intelligently answers customer questions or escalates to human agents when uncertain.

## 🚀 Features

- **RAG-Based Retrieval**: Uses sentence-transformers and FAISS for semantic search over help articles
- **Intelligent Escalation**: Automatically escalates to human agents when confidence is low
- **FastAPI Backend**: Fast, async API with automatic OpenAPI documentation
- **Google Gemini LLM**: Powered by gemini-1.5-flash for fast, accurate responses

## 📡 API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /ask` - Submit customer questions and get answers

## 🔧 Environment Variables

Configure these in your Space settings under "Repository secrets":

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key (required) | - |
| `ARTICLES_DIR` | Path to help articles | `data/articles` |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `RELEVANCE_THRESHOLD` | Minimum similarity score (0-1) | `0.5` |
| `TOP_K_CHUNKS` | Number of chunks to retrieve | `3` |
| `CHUNK_SIZE` | Characters per chunk | `500` |
| `CHUNK_OVERLAP` | Overlap between chunks | `50` |
| `LLM_MODEL` | Gemini model name | `gemini-1.5-flash` |
| `LLM_TEMPERATURE` | LLM temperature (0-1) | `0.3` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |

## 📖 Usage

### Example Request

```bash
curl -X POST https://webflow97-deployment-taskflow.hf.space/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?"}'
```

### Example Response (Answer)

```json
{
  "response_type": "answer",
  "message": "To reset your password, go to the login page and click 'Forgot Password'. Enter your email address and you'll receive a reset link.",
  "confidence_explanation": "High confidence - retrieved relevant content with similarity score 0.82",
  "sources": ["getting-started.md"]
}
```

### Example Response (Escalation)

```json
{
  "response_type": "escalation",
  "message": "I'm not certain I can answer this accurately. Let me connect you with a human support agent who can help.",
  "confidence_explanation": "Low confidence - best retrieval score was 0.42",
  "sources": null
}
```

## 📚 Interactive Documentation

Visit `/docs` for interactive API documentation powered by Swagger UI.

## 🏗️ Architecture

- **Backend**: Python FastAPI
- **Vector Store**: FAISS (in-memory) with sentence-transformers embeddings
- **LLM**: Google Gemini API (gemini-1.5-flash)
- **Deployment**: Hugging Face Spaces (Docker)

## 📝 Help Articles

The system includes help articles about TaskFlow (a fictional project management SaaS):

1. **Getting Started** - TaskFlow basics, account setup, first project
2. **Billing and Subscriptions** - Plans, payment methods, billing cycles
3. **Integrations** - Slack, GitHub, Jira integrations
4. **Team Permissions** - Roles, access control, admin settings
5. **Troubleshooting** - Common errors, login issues, performance tips

## 🔗 Links

- **Frontend**: https://escalation-api-frontend.vercel.app/
- **GitHub**: https://github.com/webflow-ai/Escalation-api
- **API Docs**: https://webflow97-deployment-taskflow.hf.space/docs

## 📄 License

MIT
