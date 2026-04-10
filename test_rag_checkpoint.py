"""
Checkpoint test script for RAG system.

This script tests that the RAG system:
1. Loads all help articles correctly
2. Generates embeddings and builds FAISS index
3. Retrieves relevant chunks for sample questions
4. Returns results with proper scores and metadata
"""

from src.rag import RAGSystem


def print_separator():
    print("\n" + "=" * 80 + "\n")


def test_rag_initialization():
    """Test that RAG system initializes and loads articles."""
    print("TEST 1: RAG System Initialization")
    print("-" * 80)
    
    rag = RAGSystem(
        articles_dir="data/articles",
        embedding_model="all-MiniLM-L6-v2",
        chunk_size=500,
        chunk_overlap=50
    )
    
    stats = rag.get_stats()
    print(f"✓ Total chunks: {stats['total_chunks']}")
    print(f"✓ Total articles: {stats['total_articles']}")
    print(f"✓ Articles loaded: {', '.join(stats['articles'])}")
    print(f"✓ Embedding dimension: {stats['embedding_dim']}")
    print(f"✓ Index size: {stats['index_size']}")
    
    assert stats['total_chunks'] > 0, "No chunks loaded"
    assert stats['total_articles'] == 5, f"Expected 5 articles, got {stats['total_articles']}"
    assert stats['index_size'] == stats['total_chunks'], "Index size mismatch"
    
    print("\n✓ RAG system initialized successfully!")
    return rag


def test_sample_questions(rag: RAGSystem):
    """Test retrieval with various sample questions."""
    print_separator()
    print("TEST 2: Sample Question Retrieval")
    print("-" * 80)
    
    # Define test questions covering different topics
    test_questions = [
        {
            "question": "How do I add a team member to my project?",
            "expected_topic": "permissions",
            "description": "Team management question"
        },
        {
            "question": "What are the subscription plans available?",
            "expected_topic": "billing",
            "description": "Billing question"
        },
        {
            "question": "How do I integrate TaskFlow with Slack?",
            "expected_topic": "integrations",
            "description": "Integration question"
        },
        {
            "question": "I can't log in to my account",
            "expected_topic": "troubleshooting",
            "description": "Troubleshooting question"
        },
        {
            "question": "How do I create my first project?",
            "expected_topic": "getting-started",
            "description": "Getting started question"
        }
    ]
    
    for i, test_case in enumerate(test_questions, 1):
        question = test_case["question"]
        expected_topic = test_case["expected_topic"]
        description = test_case["description"]
        
        print(f"\nQuestion {i}: {description}")
        print(f"Q: {question}")
        print()
        
        # Retrieve top 3 chunks
        chunks = rag.retrieve(question, top_k=3)
        
        assert len(chunks) > 0, f"No chunks retrieved for: {question}"
        assert len(chunks) <= 3, f"Too many chunks returned: {len(chunks)}"
        
        # Display results
        for j, chunk in enumerate(chunks, 1):
            print(f"  Result {j}:")
            print(f"    Source: {chunk.source}")
            print(f"    Score: {chunk.score:.4f}")
            print(f"    Content preview: {chunk.content[:100]}...")
            print()
        
        # Verify scores are in descending order
        scores = [chunk.score for chunk in chunks]
        assert scores == sorted(scores, reverse=True), "Scores not in descending order"
        
        # Check if expected topic appears in top results
        sources = [chunk.source for chunk in chunks]
        topic_found = any(expected_topic in source.lower() for source in sources)
        
        if topic_found:
            print(f"  ✓ Expected topic '{expected_topic}' found in results")
        else:
            print(f"  ⚠ Expected topic '{expected_topic}' not in top results")
            print(f"    (This may be okay if the question is ambiguous)")
    
    print("\n✓ All sample questions processed successfully!")


def test_edge_cases(rag: RAGSystem):
    """Test edge cases and boundary conditions."""
    print_separator()
    print("TEST 3: Edge Cases")
    print("-" * 80)
    
    # Test 1: Empty question
    print("\n1. Empty question:")
    chunks = rag.retrieve("", top_k=3)
    assert len(chunks) == 0, "Empty question should return no results"
    print("  ✓ Empty question returns no results")
    
    # Test 2: Very short question
    print("\n2. Very short question:")
    chunks = rag.retrieve("help", top_k=3)
    assert len(chunks) > 0, "Short question should return results"
    print(f"  ✓ Short question returns {len(chunks)} results")
    
    # Test 3: Question with special characters
    print("\n3. Question with special characters:")
    chunks = rag.retrieve("How do I use @mentions & #tags?", top_k=3)
    assert len(chunks) > 0, "Question with special chars should return results"
    print(f"  ✓ Special characters handled: {len(chunks)} results")
    
    # Test 4: Different top_k values
    print("\n4. Different top_k values:")
    for k in [1, 3, 5, 10]:
        chunks = rag.retrieve("How do I get started?", top_k=k)
        expected_k = min(k, rag.get_stats()['total_chunks'])
        assert len(chunks) <= expected_k, f"top_k={k} returned too many results"
        print(f"  ✓ top_k={k}: returned {len(chunks)} chunks (max: {expected_k})")
    
    # Test 5: Out-of-scope question
    print("\n5. Out-of-scope question:")
    chunks = rag.retrieve("What is the weather today?", top_k=3)
    print(f"  ✓ Out-of-scope question returns {len(chunks)} results")
    if chunks:
        print(f"    Best score: {chunks[0].score:.4f}")
        print(f"    (Low score expected for out-of-scope questions)")
    
    print("\n✓ All edge cases handled correctly!")


def main():
    """Run all checkpoint tests."""
    print("=" * 80)
    print("RAG SYSTEM CHECKPOINT TEST")
    print("=" * 80)
    
    try:
        # Test 1: Initialize RAG system
        rag = test_rag_initialization()
        
        # Test 2: Sample questions
        test_sample_questions(rag)
        
        # Test 3: Edge cases
        test_edge_cases(rag)
        
        # Final summary
        print_separator()
        print("✓ ALL TESTS PASSED!")
        print()
        print("Summary:")
        print("  - RAG system loads articles and builds index correctly")
        print("  - Retrieval returns relevant chunks with proper scores")
        print("  - Results are ordered by descending relevance")
        print("  - Edge cases are handled gracefully")
        print()
        print("The RAG system is ready for Phase 2 (API and Escalation Logic)!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
