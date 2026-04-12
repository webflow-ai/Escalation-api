"""
Vercel Serverless Function for handling customer support questions.
Endpoint: POST /api/ask
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
rag_system = None
llm_client = None
escalation_engine = None

def initialize_components():
    """Initialize RAG system, LLM client, and escalation engine."""
    global rag_system, llm_client, escalation_engine
    
    if rag_system is None:
        articles_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "articles"
        )
        rag_system = RAGSystem(articles_dir=articles_dir)
        llm_client = LLMClient(api_key=settings.google_api_key, model=settings.llm_model)
        escalation_engine = EscalationEngine(
            llm_client=llm_client,
            relevance_threshold=settings.relevance_threshold
        )

app = FastAPI(title="Smart Escalation API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    response_type: str
    message: str
    confidence_explanation: str
    sources: list = None

@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Process customer question and return answer or escalation.
    
    Args:
        request: QuestionRequest with 'question' field
        
    Returns:
        QuestionResponse with response_type, message, confidence_explanation, sources
    """
    try:
        # Initialize components on first request
        initialize_components()
        
        # Validate question
        if not request.question or len(request.question.strip()) == 0:
            return JSONResponse(
                status_code=400,
                content={
                    "response_type": "error",
                    "message": "Question cannot be empty",
                    "confidence_explanation": "Invalid request",
                    "sources": None
                }
            )
        
        # Retrieve relevant chunks
        chunks = rag_system.retrieve(request.question, top_k=settings.top_k_chunks)
        
        # Decide whether to answer or escalate
        decision = escalation_engine.process_question(request.question, chunks)
        
        return {
            "response_type": decision.action,
            "message": decision.message,
            "confidence_explanation": decision.confidence_explanation,
            "sources": decision.sources
        }
        
    except Exception as e:
        # Log error and return escalation response
        print(f"Error processing question: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "response_type": "escalation",
                "message": "I'm experiencing technical difficulties. Let me connect you with a human agent.",
                "confidence_explanation": f"System error occurred",
                "sources": None
            }
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "vector_store_loaded": rag_system is not None
    }

# Vercel serverless function handler
def handler(request: Request):
    """Main handler for Vercel serverless function."""
    return app(request)
