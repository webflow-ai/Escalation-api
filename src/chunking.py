"""
Text chunking module for the Smart Escalation API.

This module provides functionality to split help articles into fixed-size chunks
with overlap while preserving sentence boundaries and tracking source metadata.
"""

from typing import List, Dict, Any
import re


def chunk_text(
    text: str,
    source_article: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Split text into fixed-size chunks with overlap, preserving sentence boundaries.
    
    Args:
        text: The article text to chunk
        source_article: The filename or identifier of the source article
        chunk_size: Maximum size of each chunk in characters (default: 500)
        chunk_overlap: Number of characters to overlap between chunks (default: 50)
        
    Returns:
        List of chunk dictionaries, each containing:
            - content: The chunk text
            - source: The source article identifier
            - position: The starting character position in the original text
            - chunk_id: Sequential chunk identifier
            
    Example:
        >>> chunks = chunk_text("First sentence. Second sentence.", "test.md")
        >>> chunks[0]['content']
        'First sentence. Second sentence.'
        >>> chunks[0]['source']
        'test.md'
    """
    if not text or not text.strip():
        return []
    
    # Normalize whitespace
    text = text.strip()
    
    chunks = []
    chunk_id = 0
    start_pos = 0
    
    while start_pos < len(text):
        # Calculate end position for this chunk
        end_pos = start_pos + chunk_size
        
        # If this is the last chunk or we're at the end, take everything remaining
        if end_pos >= len(text):
            chunk_content = text[start_pos:].strip()
            if chunk_content:
                chunks.append({
                    'content': chunk_content,
                    'source': source_article,
                    'position': start_pos,
                    'chunk_id': chunk_id
                })
            break
        
        # Try to find a sentence boundary near the end position
        chunk_content = text[start_pos:end_pos]
        
        # Look for sentence-ending punctuation followed by space or end
        # Search backwards from the end to find the last complete sentence
        sentence_end = _find_sentence_boundary(chunk_content)
        
        if sentence_end > 0:
            # Found a sentence boundary, use it
            chunk_content = text[start_pos:start_pos + sentence_end].strip()
            actual_end = start_pos + sentence_end
        else:
            # No sentence boundary found, try to break at word boundary
            word_boundary = _find_word_boundary(chunk_content)
            if word_boundary > 0:
                chunk_content = text[start_pos:start_pos + word_boundary].strip()
                actual_end = start_pos + word_boundary
            else:
                # Last resort: use the full chunk_size
                chunk_content = chunk_content.strip()
                actual_end = end_pos
        
        if chunk_content:
            chunks.append({
                'content': chunk_content,
                'source': source_article,
                'position': start_pos,
                'chunk_id': chunk_id
            })
            chunk_id += 1
        
        # Move start position forward, accounting for overlap
        # Ensure we move forward by at least 1 character to avoid infinite loops
        next_start = max(actual_end - chunk_overlap, start_pos + 1)
        start_pos = next_start
    
    return chunks


def _find_sentence_boundary(text: str) -> int:
    """
    Find the position of the last sentence boundary in the text.
    
    A sentence boundary is defined as sentence-ending punctuation
    (. ! ?) followed by whitespace or end of text.
    
    Args:
        text: The text to search
        
    Returns:
        Position after the sentence-ending punctuation, or 0 if not found
    """
    # Pattern: sentence-ending punctuation followed by space or end
    # Search from the end backwards
    pattern = r'[.!?](?=\s|$)'
    matches = list(re.finditer(pattern, text))
    
    if matches:
        # Return position after the punctuation
        last_match = matches[-1]
        return last_match.end()
    
    return 0


def _find_word_boundary(text: str) -> int:
    """
    Find the position of the last word boundary in the text.
    
    A word boundary is defined as whitespace between words.
    
    Args:
        text: The text to search
        
    Returns:
        Position after the last whitespace, or 0 if not found
    """
    # Search backwards for whitespace
    for i in range(len(text) - 1, -1, -1):
        if text[i].isspace():
            # Return position after the whitespace
            return i + 1
    
    return 0
