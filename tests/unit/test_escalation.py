"""
Unit tests for the escalation engine module.

Tests escalation decision rules including threshold comparisons
and confidence explanation generation.

**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.escalation import EscalationEngine, EscalationDecision
from src.rag import RetrievedChunk
from src.llm_client import LLMClient, LLMResponse


class TestEscalationDecisionRules:
    """Test cases for escalation decision logic."""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        return Mock(spec=LLMClient)
    
    @pytest.fixture
    def engine(self, mock_llm_client):
        """Create escalation engine with default threshold."""
        return EscalationEngine(
            llm_client=mock_llm_client,
            relevance_threshold=0.5
        )
    
    def test_escalate_on_empty_chunks(self, engine):
        """Should escalate when no chunks are retrieved."""
        decision = engine.process_question("test question", [])
        
        assert decision.action == "escalation"
        assert "no relevant information" in decision.confidence_explanation.lower()
    
    def test_escalate_on_low_relevance_score(self, engine):
        """Should escalate when best relevance score is below threshold."""
        chunks = [
            RetrievedChunk(
                content="Some content",
                score=0.3,  # Below 0.5 threshold
                source="test.md",
                chunk_id=0,
                position=0
            )
        ]
        
        decision = engine.process_question("test question", chunks)
        
        assert decision.action == "escalation"
        assert "0.30" in decision.confidence_explanation or "0.3" in decision.confidence_explanation
        assert decision.sources is None
    
    def test_escalate_on_llm_uncertainty(self, engine, mock_llm_client):
        """Should escalate when LLM signals uncertainty."""
        chunks = [
            RetrievedChunk(
                content="Relevant content",
                score=0.8,  # High score
                source="test.md",
                chunk_id=0,
                position=0
            )
        ]
        
        # Mock LLM to return uncertain response
        mock_llm_client.generate_answer.return_value = LLMResponse(
            answer="I'm not certain about this.",
            uncertain=True
        )
        
        decision = engine.process_question("test question", chunks)
        
        assert decision.action == "escalation"
        assert "uncertainty" in decision.confidence_explanation.lower()
        assert decision.sources is None
    
    def test_answer_on_high_relevance(self, engine, mock_llm_client):
        """Should answer when relevance score is above threshold and LLM is confident."""
        chunks = [
            RetrievedChunk(
                content="Relevant content",
                score=0.8,
                source="billing.md",
                chunk_id=0,
                position=0
            )
        ]
        
        # Mock LLM to return confident answer
        mock_llm_client.generate_answer.return_value = LLMResponse(
            answer="Here is the answer to your question.",
            uncertain=False
        )
        
        decision = engine.process_question("test question", chunks)
        
        assert decision.action == "answer"
        assert decision.message == "Here is the answer to your question."
        assert "0.8" in decision.confidence_explanation or "0.80" in decision.confidence_explanation
        assert decision.sources == ["billing.md"]
    
    def test_threshold_boundary_below(self, engine):
        """Should escalate when score is exactly at threshold (0.5)."""
        chunks = [
            RetrievedChunk(
                content="Content",
                score=0.49,  # Just below threshold
                source="test.md",
                chunk_id=0,
                position=0
            )
        ]
        
        decision = engine.process_question("test question", chunks)
        
        assert decision.action == "escalation"
    
    def test_threshold_boundary_above(self, engine, mock_llm_client):
        """Should attempt to answer when score is above threshold."""
        chunks = [
            RetrievedChunk(
                content="Content",
                score=0.51,  # Just above threshold
                source="test.md",
                chunk_id=0,
                position=0
            )
        ]
        
        mock_llm_client.generate_answer.return_value = LLMResponse(
            answer="Answer",
            uncertain=False
        )
        
        decision = engine.process_question("test question", chunks)
        
        assert decision.action == "answer"
    
    def test_custom_threshold(self, mock_llm_client):
        """Should respect custom relevance threshold."""
        engine = EscalationEngine(
            llm_client=mock_llm_client,
            relevance_threshold=0.7  # Higher threshold
        )
        
        chunks = [
            RetrievedChunk(
                content="Content",
                score=0.6,  # Would pass 0.5 but not 0.7
                source="test.md",
                chunk_id=0,
                position=0
            )
        ]
        
        decision = engine.process_question("test question", chunks)
        
        assert decision.action == "escalation"
        assert "0.7" in decision.confidence_explanation or "0.70" in decision.confidence_explanation


class TestConfidenceExplanationGeneration:
    """Test cases for confidence explanation generation."""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        return Mock(spec=LLMClient)
    
    @pytest.fixture
    def engine(self, mock_llm_client):
        """Create escalation engine."""
        return EscalationEngine(llm_client=mock_llm_client)
    
    def test_explanation_includes_score_for_answer(self, engine, mock_llm_client):
        """Confidence explanation for answers should include relevance score."""
        chunks = [
            RetrievedChunk(
                content="Content",
                score=0.85,
                source="test.md",
                chunk_id=0,
                position=0
            )
        ]
        
        mock_llm_client.generate_answer.return_value = LLMResponse(
            answer="Answer",
            uncertain=False
        )
        
        decision = engine.process_question("test", chunks)
        
        assert "0.85" in decision.confidence_explanation
        assert "confidence" in decision.confidence_explanation.lower()
    
    def test_explanation_includes_source_for_answer(self, engine, mock_llm_client):
        """Confidence explanation should mention source article."""
        chunks = [
            RetrievedChunk(
                content="Content",
                score=0.8,
                source="billing.md",
                chunk_id=0,
                position=0
            )
        ]
        
        mock_llm_client.generate_answer.return_value = LLMResponse(
            answer="Answer",
            uncertain=False
        )
        
        decision = engine.process_question("test", chunks)
        
        assert "billing.md" in decision.confidence_explanation
    
    def test_explanation_for_multiple_sources(self, engine, mock_llm_client):
        """Should mention multiple sources in explanation."""
        chunks = [
            RetrievedChunk(content="C1", score=0.8, source="billing.md", chunk_id=0, position=0),
            RetrievedChunk(content="C2", score=0.7, source="permissions.md", chunk_id=1, position=0)
        ]
        
        mock_llm_client.generate_answer.return_value = LLMResponse(
            answer="Answer",
            uncertain=False
        )
        
        decision = engine.process_question("test", chunks)
        
        # Should mention multiple articles
        assert "2" in decision.confidence_explanation or "multiple" in decision.confidence_explanation.lower()
    
    def test_explanation_for_low_score_escalation(self, engine):
        """Escalation explanation should mention low score."""
        chunks = [
            RetrievedChunk(
                content="Content",
                score=0.3,
                source="test.md",
                chunk_id=0,
                position=0
            )
        ]
        
        decision = engine.process_question("test", chunks)
        
        assert decision.action == "escalation"
        assert "0.3" in decision.confidence_explanation or "0.30" in decision.confidence_explanation
        assert "threshold" in decision.confidence_explanation.lower()
    
    def test_explanation_for_llm_uncertainty(self, engine, mock_llm_client):
        """Escalation explanation should mention LLM uncertainty."""
        chunks = [
            RetrievedChunk(content="Content", score=0.8, source="test.md", chunk_id=0, position=0)
        ]
        
        mock_llm_client.generate_answer.return_value = LLMResponse(
            answer="Not sure",
            uncertain=True
        )
        
        decision = engine.process_question("test", chunks)
        
        assert decision.action == "escalation"
        assert "uncertainty" in decision.confidence_explanation.lower()
    
    def test_explanation_for_no_chunks(self, engine):
        """Escalation explanation should mention no relevant information."""
        decision = engine.process_question("test", [])
        
        assert decision.action == "escalation"
        assert "no relevant" in decision.confidence_explanation.lower()


class TestSourceExtraction:
    """Test cases for source reference extraction."""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        return Mock(spec=LLMClient)
    
    @pytest.fixture
    def engine(self, mock_llm_client):
        """Create escalation engine."""
        return EscalationEngine(llm_client=mock_llm_client)
    
    def test_sources_included_for_answers(self, engine, mock_llm_client):
        """Answer responses should include source references."""
        chunks = [
            RetrievedChunk(content="C", score=0.8, source="billing.md", chunk_id=0, position=0)
        ]
        
        mock_llm_client.generate_answer.return_value = LLMResponse(
            answer="Answer",
            uncertain=False
        )
        
        decision = engine.process_question("test", chunks)
        
        assert decision.sources is not None
        assert "billing.md" in decision.sources
    
    def test_sources_not_included_for_escalations(self, engine):
        """Escalation responses should not include sources."""
        chunks = [
            RetrievedChunk(content="C", score=0.2, source="test.md", chunk_id=0, position=0)
        ]
        
        decision = engine.process_question("test", chunks)
        
        assert decision.action == "escalation"
        assert decision.sources is None
    
    def test_multiple_sources_deduplicated(self, engine, mock_llm_client):
        """Should deduplicate sources from multiple chunks."""
        chunks = [
            RetrievedChunk(content="C1", score=0.8, source="billing.md", chunk_id=0, position=0),
            RetrievedChunk(content="C2", score=0.7, source="billing.md", chunk_id=1, position=100),
            RetrievedChunk(content="C3", score=0.6, source="permissions.md", chunk_id=0, position=0)
        ]
        
        mock_llm_client.generate_answer.return_value = LLMResponse(
            answer="Answer",
            uncertain=False
        )
        
        decision = engine.process_question("test", chunks)
        
        assert len(decision.sources) == 2
        assert "billing.md" in decision.sources
        assert "permissions.md" in decision.sources
    
    def test_sources_sorted(self, engine, mock_llm_client):
        """Sources should be sorted alphabetically."""
        chunks = [
            RetrievedChunk(content="C1", score=0.8, source="permissions.md", chunk_id=0, position=0),
            RetrievedChunk(content="C2", score=0.7, source="billing.md", chunk_id=0, position=0)
        ]
        
        mock_llm_client.generate_answer.return_value = LLMResponse(
            answer="Answer",
            uncertain=False
        )
        
        decision = engine.process_question("test", chunks)
        
        assert decision.sources == ["billing.md", "permissions.md"]


class TestErrorHandling:
    """Test cases for error handling in escalation engine."""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        return Mock(spec=LLMClient)
    
    @pytest.fixture
    def engine(self, mock_llm_client):
        """Create escalation engine."""
        return EscalationEngine(llm_client=mock_llm_client)
    
    def test_escalate_on_llm_error(self, engine, mock_llm_client):
        """Should escalate gracefully when LLM call fails."""
        chunks = [
            RetrievedChunk(content="C", score=0.8, source="test.md", chunk_id=0, position=0)
        ]
        
        mock_llm_client.generate_answer.side_effect = Exception("API error")
        
        decision = engine.process_question("test", chunks)
        
        assert decision.action == "escalation"
        assert decision.sources is None
    
    def test_escalate_on_timeout(self, engine, mock_llm_client):
        """Should escalate with timeout message when LLM times out."""
        chunks = [
            RetrievedChunk(content="C", score=0.8, source="test.md", chunk_id=0, position=0)
        ]
        
        mock_llm_client.generate_answer.side_effect = RuntimeError("Request timeout")
        
        decision = engine.process_question("test", chunks)
        
        assert decision.action == "escalation"
        assert "timeout" in decision.confidence_explanation.lower()
    
    def test_escalate_on_rate_limit(self, engine, mock_llm_client):
        """Should escalate with rate limit message."""
        chunks = [
            RetrievedChunk(content="C", score=0.8, source="test.md", chunk_id=0, position=0)
        ]
        
        mock_llm_client.generate_answer.side_effect = RuntimeError("Rate limit exceeded")
        
        decision = engine.process_question("test", chunks)
        
        assert decision.action == "escalation"
        assert "rate limit" in decision.confidence_explanation.lower() or "busy" in decision.confidence_explanation.lower()
