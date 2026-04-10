"""
Unit tests for the text chunking module.
"""

import pytest
from src.chunking import chunk_text, _find_sentence_boundary, _find_word_boundary


class TestChunkText:
    """Test cases for the chunk_text function."""
    
    def test_empty_text_returns_empty_list(self):
        """Empty text should return no chunks."""
        result = chunk_text("", "test.md")
        assert result == []
    
    def test_whitespace_only_returns_empty_list(self):
        """Whitespace-only text should return no chunks."""
        result = chunk_text("   \n\t  ", "test.md")
        assert result == []
    
    def test_short_text_returns_single_chunk(self):
        """Text shorter than chunk_size should return single chunk."""
        text = "This is a short text."
        result = chunk_text(text, "test.md", chunk_size=500)
        
        assert len(result) == 1
        assert result[0]['content'] == text
        assert result[0]['source'] == "test.md"
        assert result[0]['position'] == 0
        assert result[0]['chunk_id'] == 0
    
    def test_preserves_sentence_boundaries(self):
        """Chunks should end at sentence boundaries when possible."""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        result = chunk_text(text, "test.md", chunk_size=30, chunk_overlap=5)
        
        # Each chunk should end with sentence-ending punctuation
        for chunk in result[:-1]:  # All but last chunk
            content = chunk['content']
            assert content[-1] in '.!?' or content.endswith('.')
    
    def test_chunk_overlap_maintained(self):
        """Consecutive chunks should have specified overlap."""
        text = "A" * 1000  # Long text without sentence boundaries
        result = chunk_text(text, "test.md", chunk_size=100, chunk_overlap=20)
        
        assert len(result) > 1
        # Check that chunks are created (overlap logic is working)
        for i in range(len(result) - 1):
            # Verify position progression accounts for overlap
            current_end = result[i]['position'] + len(result[i]['content'])
            next_start = result[i + 1]['position']
            # Next chunk should start before current chunk ends (overlap)
            assert next_start < current_end
    
    def test_no_word_splitting(self):
        """Chunks should not split words mid-character."""
        text = "The quick brown fox jumps over the lazy dog. " * 20
        result = chunk_text(text, "test.md", chunk_size=50, chunk_overlap=10)
        
        for chunk in result:
            content = chunk['content']
            # Check that chunks don't end with partial words (unless at sentence end)
            if len(content) > 0 and content[-1] not in '.!? ':
                # If not ending with punctuation or space, should be end of text
                assert chunk == result[-1]
    
    def test_metadata_tracking(self):
        """Each chunk should have correct metadata."""
        text = "First sentence. Second sentence. Third sentence."
        result = chunk_text(text, "billing.md", chunk_size=25, chunk_overlap=5)
        
        for i, chunk in enumerate(result):
            assert 'content' in chunk
            assert 'source' in chunk
            assert 'position' in chunk
            assert 'chunk_id' in chunk
            assert chunk['source'] == "billing.md"
            assert chunk['chunk_id'] == i
            assert chunk['position'] >= 0
    
    def test_default_parameters(self):
        """Test with default chunk_size and overlap."""
        text = "A" * 1000
        result = chunk_text(text, "test.md")
        
        assert len(result) > 0
        # First chunk should be around 500 chars (default chunk_size)
        assert len(result[0]['content']) <= 500
    
    def test_custom_chunk_size(self):
        """Test with custom chunk size."""
        text = "This is a test. " * 50
        result = chunk_text(text, "test.md", chunk_size=100, chunk_overlap=10)
        
        for chunk in result[:-1]:  # All but last
            # Chunks should not exceed chunk_size significantly
            assert len(chunk['content']) <= 100
    
    def test_position_tracking(self):
        """Position should track location in original text."""
        text = "First sentence. Second sentence. Third sentence."
        result = chunk_text(text, "test.md", chunk_size=20, chunk_overlap=5)
        
        # Positions should be non-decreasing
        positions = [chunk['position'] for chunk in result]
        assert positions == sorted(positions)
        
        # First chunk should start at position 0
        assert result[0]['position'] == 0


class TestFindSentenceBoundary:
    """Test cases for _find_sentence_boundary helper function."""
    
    def test_finds_period_boundary(self):
        """Should find sentence ending with period."""
        text = "First sentence. Second"
        pos = _find_sentence_boundary(text)
        assert pos == 15  # Position after "sentence."
    
    def test_finds_exclamation_boundary(self):
        """Should find sentence ending with exclamation mark."""
        text = "Hello world! How are"
        pos = _find_sentence_boundary(text)
        assert pos == 12  # Position after "world!"
    
    def test_finds_question_boundary(self):
        """Should find sentence ending with question mark."""
        text = "What is this? Another"
        pos = _find_sentence_boundary(text)
        assert pos == 13  # Position after "this?"
    
    def test_finds_last_boundary(self):
        """Should find the last sentence boundary."""
        text = "First. Second. Third"
        pos = _find_sentence_boundary(text)
        assert pos == 14  # Position after "Second."
    
    def test_no_boundary_returns_zero(self):
        """Should return 0 when no sentence boundary found."""
        text = "No sentence ending here"
        pos = _find_sentence_boundary(text)
        assert pos == 0
    
    def test_boundary_at_end(self):
        """Should handle sentence boundary at text end."""
        text = "Complete sentence."
        pos = _find_sentence_boundary(text)
        assert pos == 18  # Position after "sentence."


class TestFindWordBoundary:
    """Test cases for _find_word_boundary helper function."""
    
    def test_finds_last_space(self):
        """Should find the last whitespace."""
        text = "Hello world test"
        pos = _find_word_boundary(text)
        assert pos == 12  # Position after "world "
    
    def test_no_space_returns_zero(self):
        """Should return 0 when no whitespace found."""
        text = "NoSpacesHere"
        pos = _find_word_boundary(text)
        assert pos == 0
    
    def test_multiple_spaces(self):
        """Should find the last whitespace with multiple spaces."""
        text = "One two three four"
        pos = _find_word_boundary(text)
        assert pos == 14  # Position after "three "
    
    def test_trailing_space(self):
        """Should handle trailing whitespace."""
        text = "Hello world "
        pos = _find_word_boundary(text)
        assert pos == 12  # Position after last space
