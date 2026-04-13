"""
Vercel Serverless Function - Main API endpoint
Handles: POST /api
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag import RAGSystem
from src.escalation import EscalationEngine
from src.llm_client import LLMClient
from src.config import Settings

# Global components (cached across invocations)
_settings = None
_rag_system = None
_llm_client = None
_escalation_engine = None

def get_components():
    """Initialize and return components (cached)."""
    global _settings, _rag_system, _llm_client, _escalation_engine
    
    if _rag_system is None:
        _settings = Settings()
        articles_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "articles"
        )
        _rag_system = RAGSystem(articles_dir=articles_dir)
        _llm_client = LLMClient(api_key=_settings.google_api_key, model=_settings.llm_model)
        _escalation_engine = EscalationEngine(
            llm_client=_llm_client,
            relevance_threshold=_settings.relevance_threshold
        )
    
    return _settings, _rag_system, _llm_client, _escalation_engine

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler."""
    
    def do_POST(self):
        """Handle POST requests."""
        try:
            settings, rag_system, llm_client, escalation_engine = get_components()
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            # Parse JSON
            try:
                data = json.loads(body)
                question = data.get('question', '').strip()
            except json.JSONDecodeError:
                self.send_error_response(400, "Invalid JSON")
                return
            
            # Validate question
            if not question:
                self.send_error_response(400, "Question cannot be empty")
                return
            
            # Retrieve relevant chunks
            chunks = rag_system.retrieve(question, top_k=settings.top_k_chunks)
            
            # Decide whether to answer or escalate
            decision = escalation_engine.process_question(question, chunks)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response = {
                "response_type": decision.action,
                "message": decision.message,
                "confidence_explanation": decision.confidence_explanation,
                "sources": decision.sources
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"Error processing question: {str(e)}")
            import traceback
            traceback.print_exc()
            self.send_error_response(500, "Internal server error")
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests (health check)."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "message": "Smart Escalation API is running",
            "vector_store_loaded": _rag_system is not None
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def send_error_response(self, status_code, message):
        """Send error response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "response_type": "error",
            "message": message,
            "confidence_explanation": "Request error",
            "sources": None
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
