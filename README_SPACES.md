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

AI-powered L1 customer support system with intelligent escalation.

## Features

- RAG-based retrieval using sentence-transformers and FAISS
- Intelligent escalation to human agents
- Google Gemini LLM integration
- FastAPI backend with automatic documentation

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /ask` - Submit customer questions

## Environment Variables

Configure these in your Space settings:

- `GOOGLE_API_KEY` - Your Google Gemini API key (required)
- `ARTICLES_DIR` - Path to help articles (default: data/articles)
- `EMBEDDING_MODEL` - Sentence transformer model (default: all-MiniLM-L6-v2)
- `RELEVANCE_THRESHOLD` - Minimum similarity score (default: 0.5)
- `TOP_K_CHUNKS` - Number of chunks to retrieve (default: 3)
- `LLM_MODEL` - Gemini model name (default: gemini-1.5-flash)
- `CORS_ORIGINS` - Allowed CORS origins

## Usage

```bash
curl -X POST https://YOUR_USERNAME-escalation-api.hf.space/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?"}'
```

## Documentation

Visit `/docs` for interactive API documentation.
