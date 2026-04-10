"""
FastAPI application for the Smart Escalation API.

This module provides the main API endpoint for processing customer questions
and returning answers or escalation messages.
"""

import os
from typing import Literal, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

from src.rag import RAGSystem
from src.llm_client import LLMClient
from src.escalation import EscalationEngine


# Load environment variables
load_dotenv()


# Pydantic models for request/response
class QuestionRequest(BaseModel):
    """Request model for customer questions."""
    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Customer question (1-500 characters)"
    )
    
    @validator('question')
    def question_not_empty(cls, v):
        """Validate that question is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Question cannot be empty or whitespace only")
        return v.strip()


class QuestionResponse(BaseModel):
    """Response model for API answers."""
    response_type: Literal["answer", "escalation"] = Field(
        ...,
        description="Type of response: 'answer' or 'escalation'"
    )
    message: str = Field(
        ...,
        description="Answer text or escalation message"
    )
    confidence_explanation: str = Field(
        ...,
        description="Explanation of why the system answered or escalated"
    )
    sources: Optional[List[str]] = Field(
        None,
        description="List of source help articles (only for answers)"
    )


# Global instances (initialized on startup)
rag_system: Optional[RAGSystem] = None
escalation_engine: Optional[EscalationEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Initializes RAG system, LLM client, and escalation engine on startup.
    """
    global rag_system, escalation_engine
    
    print("Starting Smart Escalation API...")
    
    # Load configuration from environment
    articles_dir = os.getenv("ARTICLES_DIR", "data/articles")
    embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    relevance_threshold = float(os.getenv("RELEVANCE_THRESHOLD", "0.5"))
    top_k_chunks = int(os.getenv("TOP_K_CHUNKS", "3"))
    chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))
    llm_model = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    
    try:
        # Initialize RAG system
        print(f"Initializing RAG system with articles from {articles_dir}...")
        rag_system = RAGSystem(
            articles_dir=articles_dir,
            embedding_model=embedding_model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Initialize LLM client
        print(f"Initializing LLM client with model {llm_model}...")
        llm_client = LLMClient(
            model_name=llm_model,
            temperature=llm_temperature
        )
        
        # Initialize escalation engine
        print("Initializing escalation engine...")
        escalation_engine = EscalationEngine(
            llm_client=llm_client,
            relevance_threshold=relevance_threshold
        )
        
        # Store top_k for use in endpoint
        app.state.top_k_chunks = top_k_chunks
        
        print("✓ Smart Escalation API ready!")
        print(f"  - {rag_system.get_stats()['total_chunks']} chunks from {rag_system.get_stats()['total_articles']} articles")
        print(f"  - Relevance threshold: {relevance_threshold}")
        print(f"  - Top-k retrieval: {top_k_chunks}")
        
    except Exception as e:
        print(f"✗ Failed to initialize API: {str(e)}")
        raise
    
    yield
    
    # Cleanup (if needed)
    print("Shutting down Smart Escalation API...")


# Create FastAPI app
app = FastAPI(
    title="Smart Escalation API",
    description="AI-powered L1 customer support system with intelligent escalation",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Smart Escalation API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "ask": "/ask (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if rag_system is None or escalation_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System not initialized"
        )
    
    stats = rag_system.get_stats()
    return {
        "status": "healthy",
        "rag_system": {
            "total_chunks": stats["total_chunks"],
            "total_articles": stats["total_articles"]
        }
    }


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest) -> QuestionResponse:
    """
    Process customer question and return answer or escalation.
    
    This endpoint:
    1. Retrieves relevant help article chunks using RAG
    2. Evaluates retrieval quality
    3. Generates answer using LLM or escalates to human agent
    4. Returns structured response with confidence explanation
    
    Args:
        request: QuestionRequest with customer question
        
    Returns:
        QuestionResponse with answer/escalation and confidence explanation
        
    Raises:
        HTTPException: 400 for invalid requests, 500 for server errors
    """
    # Validate system is initialized
    if rag_system is None or escalation_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System not initialized. Please try again later."
        )
    
    try:
        # Get top_k from app state
        top_k = app.state.top_k_chunks
        
        # Step 1: Retrieve relevant chunks
        retrieved_chunks = rag_system.retrieve(
            question=request.question,
            top_k=top_k
        )
        
        # Step 2: Process question through escalation engine
        decision = escalation_engine.process_question(
            question=request.question,
            retrieved_chunks=retrieved_chunks
        )
        
        # Step 3: Build and return response
        return QuestionResponse(
            response_type=decision.action,
            message=decision.message,
            confidence_explanation=decision.confidence_explanation,
            sources=decision.sources
        )
        
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    
    except Exception as e:
        # Handle unexpected errors
        print(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your question. Please try again."
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return {
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": ["/", "/health", "/ask"]
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }
