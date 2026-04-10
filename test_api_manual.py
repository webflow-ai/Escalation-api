"""Manual test script for debugging API issues."""

import os
from dotenv import load_dotenv
from src.rag import RAGSystem
from src.llm_client import LLMClient
from src.escalation import EscalationEngine

# Load environment
load_dotenv()

print("Testing API components...")
print(f"API Key present: {bool(os.getenv('GOOGLE_API_KEY'))}")
print(f"API Key value: {os.getenv('GOOGLE_API_KEY')[:20]}..." if os.getenv('GOOGLE_API_KEY') else "None")

# Initialize RAG
print("\n1. Initializing RAG system...")
rag = RAGSystem("data/articles")
print(f"   ✓ Loaded {rag.get_stats()['total_chunks']} chunks")

# Test retrieval
print("\n2. Testing retrieval...")
question = "What subscription plans are available?"
chunks = rag.retrieve(question, top_k=3)
print(f"   ✓ Retrieved {len(chunks)} chunks")
for i, chunk in enumerate(chunks):
    print(f"   Chunk {i+1}: score={chunk.score:.3f}, source={chunk.source}")
    print(f"   Content: {chunk.content[:100]}...")

# Test LLM
print("\n3. Testing LLM client...")
try:
    llm = LLMClient(model_name="gemini-2.5-flash")
    print("   ✓ LLM client initialized")
    
    # Try to generate answer
    print("\n4. Generating answer...")
    chunk_contents = [c.content for c in chunks]
    response = llm.generate_answer(question, chunk_contents)
    print(f"   ✓ Answer generated")
    print(f"   Uncertain: {response.uncertain}")
    print(f"   Answer: {response.answer[:200]}...")
    
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
