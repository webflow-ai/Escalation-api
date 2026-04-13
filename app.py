"""
Hugging Face Spaces entry point for Smart Escalation API.
This file is required for Hugging Face Spaces deployment.
"""

import os
import uvicorn
from src.main import app

if __name__ == "__main__":
    # Hugging Face Spaces uses port 7860 by default
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
