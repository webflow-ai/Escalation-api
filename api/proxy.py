"""
Lightweight Vercel Serverless Function - API Gateway Pattern
This proxies requests to an external ML backend (deployed elsewhere)
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error

# External ML backend URL (set in Vercel environment variables)
ML_BACKEND_URL = os.getenv("ML_BACKEND_URL", "")

class handler(BaseHTTPRequestHandler):
    """Lightweight proxy handler for Vercel."""
    
    def do_POST(self):
        """Proxy POST requests to ML backend."""
        if not ML_BACKEND_URL:
            self.send_error_response(503, "ML backend not configured")
            return
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Forward to ML backend
            req = urllib.request.Request(
                f"{ML_BACKEND_URL}/ask",
                data=body,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read()
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(response_data)
                
        except urllib.error.HTTPError as e:
            self.send_error_response(e.code, f"Backend error: {e.reason}")
        except urllib.error.URLError as e:
            self.send_error_response(503, "ML backend unavailable")
        except Exception as e:
            print(f"Proxy error: {str(e)}")
            self.send_error_response(500, "Proxy error")
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Health check."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "backend_configured": bool(ML_BACKEND_URL)
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
            "confidence_explanation": "Service error",
            "sources": None
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
