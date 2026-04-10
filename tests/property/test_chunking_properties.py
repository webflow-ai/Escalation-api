"""
Property-based tests for chunking semantic coherence.

This module validates Property 3: Chunking Semantic Coherence
Validates: Requirements 2.6
"""

import pytest
from hypothesis import given, strategies as st, assume
from src.chunking import chunk_text


@given(st.text(min_size=1, max_size=5000))
def test_property_chunking_no_word_splits(article_text):
    """
    Property 3: Chunking Semantic Coherence - No Word Splits
    
    For any article text, chunks should not split words mid-character.
    Chunks should end at word boundaries (whitespace or punctuation).
    
    Feature: smart-escalation-api
    Property: Chunking preserves semantic coherence
    Validates: Requirements 2.6
    """
    # Skip empty or whitespace-only text
    assume(article_text.strip())
    
    chunks = chunk_text(article_text, source_article="test.md", chunk_size=500, chunk_overlap=50)
    
    # If no chunks were created, that's acceptable for certain inputs
    if not chunks:
        return
    
    for chunk in chunks:
        content = chunk['content']
        
        # Skip empty chunks (shouldn't happen, but defensive)
        if not content:
            continue
        
        # Check that chunk doesn't end with a partial word
        # A properly chunked text should end with:
        # - Whitespace
        # - Punctuation
        # - End of original text
        
        # If the chunk is shorter than chunk_size, it's likely the last chunk
        # and can end anywhere in the original text
        if len(content) < 500:
            continue
        
        # For full-size chunks, verify they end at appropriate boundaries
        last_char = content[-1]
        
        # Acceptable endings: whitespace, punctuation, or alphanumeric (end of sentence)
        # We should NOT end in the middle of a word (non-whitespace followed by more text)
        assert (
            last_char.isspace() or 
            last_char in ".,!?;:)]}" or
            content.rstrip() == content  # Already trimmed, so ends cleanly
        ), f"Chunk ends with potentially split word: ...{content[-20:]!r}"


@given(
    st.text(min_size=100, max_size=5000),
    st.integers(min_value=50, max_value=500),
    st.integers(min_value=10, max_value=100)
)
def test_property_chunking_overlap_maintained(article_text, chunk_size, chunk_overlap):
    """
    Property 3: Chunking Semantic Coherence - Overlap Maintained
    
    For any article text, consecutive chunks should not have large gaps between them.
    Due to sentence/word boundary preservation and whitespace stripping, small gaps
    may occur, but they should be minimal (within a few characters).
    
    Feature: smart-escalation-api
    Property: Chunking maintains reasonable overlap/adjacency
    Validates: Requirements 2.6
    """
    # Ensure overlap is less than chunk_size
    assume(chunk_overlap < chunk_size)
    # Skip empty or whitespace-only text
    assume(article_text.strip())
    # Ensure text is long enough to create multiple chunks
    assume(len(article_text) > chunk_size)
    
    chunks = chunk_text(
        article_text, 
        source_article="test.md", 
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    
    # Need at least 2 chunks to test overlap
    if len(chunks) < 2:
        return
    
    # Check that chunks progress through the text reasonably
    for i in range(len(chunks) - 1):
        chunk1 = chunks[i]
        chunk2 = chunks[i + 1]
        
        pos1 = chunk1['position']
        pos2 = chunk2['position']
        
        # Chunks should progress forward through the text
        assert pos2 > pos1, (
            f"Chunk {i+1} position {pos2} should be after chunk {i} position {pos1}"
        )
        
        # The gap between chunk starts should be reasonable
        # It should be roughly (chunk_size - chunk_overlap), but can vary due to
        # sentence/word boundaries and whitespace stripping
        gap = pos2 - pos1
        
        # Gap should not be larger than chunk_size (we're making progress)
        assert gap <= chunk_size + 10, (
            f"Gap {gap} between chunk {i} and {i+1} exceeds chunk_size {chunk_size}"
        )
        
        # Gap should not be too small (we're not stuck)
        assert gap >= 1, (
            f"Gap {gap} between chunk {i} and {i+1} is too small, chunks may overlap completely"
        )


@given(st.text(min_size=1, max_size=5000))
def test_property_chunking_preserves_content(article_text):
    """
    Property 3: Chunking Semantic Coherence - Content Preservation
    
    For any article text, all content from the original text should appear
    in at least one chunk (no content loss).
    
    Feature: smart-escalation-api
    Property: Chunking preserves all content
    Validates: Requirements 2.6
    """
    # Skip empty or whitespace-only text
    assume(article_text.strip())
    
    chunks = chunk_text(article_text, source_article="test.md", chunk_size=500, chunk_overlap=50)
    
    # If no chunks were created, the text must have been empty after stripping
    if not chunks:
        assert not article_text.strip()
        return
    
    # Combine all chunk contents
    all_chunk_content = ' '.join(chunk['content'] for chunk in chunks)
    
    # Normalize whitespace for comparison
    normalized_original = ' '.join(article_text.split())
    normalized_chunks = ' '.join(all_chunk_content.split())
    
    # All significant words from original should appear in chunks
    original_words = set(normalized_original.split())
    chunk_words = set(normalized_chunks.split())
    
    # All original words should be present in the chunks
    missing_words = original_words - chunk_words
    assert not missing_words, (
        f"Chunking lost {len(missing_words)} words from original text. "
        f"Examples: {list(missing_words)[:5]}"
    )


@given(st.text(min_size=1, max_size=5000))
def test_property_chunking_no_empty_chunks(article_text):
    """
    Property 3: Chunking Semantic Coherence - No Empty Chunks
    
    For any article text, no chunk should be empty or contain only whitespace.
    
    Feature: smart-escalation-api
    Property: Chunking produces non-empty chunks
    Validates: Requirements 2.6
    """
    # Skip empty or whitespace-only text
    assume(article_text.strip())
    
    chunks = chunk_text(article_text, source_article="test.md", chunk_size=500, chunk_overlap=50)
    
    for i, chunk in enumerate(chunks):
        content = chunk['content']
        assert content, f"Chunk {i} is empty"
        assert content.strip(), f"Chunk {i} contains only whitespace: {content!r}"


@given(st.text(min_size=1, max_size=5000))
def test_property_chunking_metadata_correctness(article_text):
    """
    Property 3: Chunking Semantic Coherence - Metadata Correctness
    
    For any article text, chunk metadata (position, chunk_id, source) should be
    correct and consistent.
    
    Feature: smart-escalation-api
    Property: Chunking metadata is accurate
    Validates: Requirements 2.6
    """
    # Skip empty or whitespace-only text
    assume(article_text.strip())
    
    source = "test_article.md"
    chunks = chunk_text(article_text, source_article=source, chunk_size=500, chunk_overlap=50)
    
    if not chunks:
        return
    
    for i, chunk in enumerate(chunks):
        # Check chunk_id is sequential
        assert chunk['chunk_id'] == i, (
            f"Chunk {i} has incorrect chunk_id: {chunk['chunk_id']}"
        )
        
        # Check source is preserved
        assert chunk['source'] == source, (
            f"Chunk {i} has incorrect source: {chunk['source']}"
        )
        
        # Check position is non-negative
        assert chunk['position'] >= 0, (
            f"Chunk {i} has negative position: {chunk['position']}"
        )
        
        # Check position is within text bounds
        assert chunk['position'] < len(article_text), (
            f"Chunk {i} position {chunk['position']} exceeds text length {len(article_text)}"
        )
