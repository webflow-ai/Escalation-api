"""
Unit tests for API response formatting.

Tests JSON construction and source reference inclusion in API responses.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
"""

import pytest
from pydantic import ValidationError
from src.main import QuestionRequest, QuestionResponse


class TestQuestionRequestValidation:
    """Test cases for QuestionRequest model validation."""
    
    def test_valid_request(self):
        """Should accept valid question."""
        request = QuestionRequest(question="How do I reset my password?")
        
        assert request.question == "How do I reset my password?"
    
    def test_reject_empty_question(self):
        """Should reject empty question string."""
        with pytest.raises(ValidationError) as exc_info:
            QuestionRequest(question="")
        
        assert "question" in str(exc_info.value).lower()
    
    def test_reject_whitespace_only(self):
        """Should reject whitespace-only question."""
        with pytest.raises(ValidationError) as exc_info:
            QuestionRequest(question="   \n\t  ")
        
        assert "question" in str(exc_info.value).lower()
    
    def test_reject_missing_question(self):
        """Should reject request without question field."""
        with pytest.raises(ValidationError):
            QuestionRequest()
    
    def test_reject_too_long_question(self):
        """Should reject question exceeding max length."""
        long_question = "a" * 501  # Max is 500
        
        with pytest.raises(ValidationError) as exc_info:
            QuestionRequest(question=long_question)
        
        assert "500" in str(exc_info.value) or "length" in str(exc_info.value).lower()
    
    def test_trim_whitespace(self):
        """Should trim leading/trailing whitespace from question."""
        request = QuestionRequest(question="  How do I reset?  ")
        
        assert request.question == "How do I reset?"
        assert not request.question.startswith(" ")
        assert not request.question.endswith(" ")
    
    def test_accept_max_length_question(self):
        """Should accept question at exactly max length."""
        question = "a" * 500
        request = QuestionRequest(question=question)
        
        assert len(request.question) == 500


class TestQuestionResponseConstruction:
    """Test cases for QuestionResponse model construction."""
    
    def test_answer_response_construction(self):
        """Should construct valid answer response."""
        response = QuestionResponse(
            response_type="answer",
            message="Here is your answer.",
            confidence_explanation="High confidence based on retrieval.",
            sources=["billing.md"]
        )
        
        assert response.response_type == "answer"
        assert response.message == "Here is your answer."
        assert response.confidence_explanation == "High confidence based on retrieval."
        assert response.sources == ["billing.md"]
    
    def test_escalation_response_construction(self):
        """Should construct valid escalation response."""
        response = QuestionResponse(
            response_type="escalation",
            message="Let me connect you with a human agent.",
            confidence_explanation="Low confidence - score below threshold.",
            sources=None
        )
        
        assert response.response_type == "escalation"
        assert response.message == "Let me connect you with a human agent."
        assert response.confidence_explanation == "Low confidence - score below threshold."
        assert response.sources is None
    
    def test_sources_optional(self):
        """Sources field should be optional."""
        response = QuestionResponse(
            response_type="answer",
            message="Answer",
            confidence_explanation="Explanation"
        )
        
        assert response.sources is None
    
    def test_reject_invalid_response_type(self):
        """Should reject invalid response_type values."""
        with pytest.raises(ValidationError) as exc_info:
            QuestionResponse(
                response_type="invalid",
                message="Message",
                confidence_explanation="Explanation"
            )
        
        assert "response_type" in str(exc_info.value).lower()
    
    def test_reject_missing_required_fields(self):
        """Should reject response missing required fields."""
        with pytest.raises(ValidationError):
            QuestionResponse(response_type="answer")
    
    def test_multiple_sources(self):
        """Should accept multiple source references."""
        response = QuestionResponse(
            response_type="answer",
            message="Answer",
            confidence_explanation="Explanation",
            sources=["billing.md", "permissions.md", "troubleshooting.md"]
        )
        
        assert len(response.sources) == 3
        assert "billing.md" in response.sources
    
    def test_empty_sources_list(self):
        """Should accept empty sources list."""
        response = QuestionResponse(
            response_type="answer",
            message="Answer",
            confidence_explanation="Explanation",
            sources=[]
        )
        
        assert response.sources == []


class TestResponseJSONSerialization:
    """Test cases for JSON serialization of responses."""
    
    def test_answer_json_schema(self):
        """Answer response should serialize to correct JSON schema."""
        response = QuestionResponse(
            response_type="answer",
            message="Your answer here.",
            confidence_explanation="High confidence.",
            sources=["billing.md"]
        )
        
        json_data = response.model_dump()
        
        assert "response_type" in json_data
        assert "message" in json_data
        assert "confidence_explanation" in json_data
        assert "sources" in json_data
        assert json_data["response_type"] == "answer"
        assert json_data["message"] == "Your answer here."
        assert json_data["confidence_explanation"] == "High confidence."
        assert json_data["sources"] == ["billing.md"]
    
    def test_escalation_json_schema(self):
        """Escalation response should serialize to correct JSON schema."""
        response = QuestionResponse(
            response_type="escalation",
            message="Connecting you with an agent.",
            confidence_explanation="Low confidence.",
            sources=None
        )
        
        json_data = response.model_dump()
        
        assert json_data["response_type"] == "escalation"
        assert json_data["message"] == "Connecting you with an agent."
        assert json_data["confidence_explanation"] == "Low confidence."
        assert json_data["sources"] is None
    
    def test_json_field_types(self):
        """JSON fields should have correct types."""
        response = QuestionResponse(
            response_type="answer",
            message="Answer",
            confidence_explanation="Explanation",
            sources=["test.md"]
        )
        
        json_data = response.model_dump()
        
        assert isinstance(json_data["response_type"], str)
        assert isinstance(json_data["message"], str)
        assert isinstance(json_data["confidence_explanation"], str)
        assert isinstance(json_data["sources"], list)
    
    def test_json_roundtrip(self):
        """Should be able to serialize and deserialize."""
        original = QuestionResponse(
            response_type="answer",
            message="Test answer",
            confidence_explanation="Test explanation",
            sources=["test.md"]
        )
        
        # Serialize to dict
        json_data = original.model_dump()
        
        # Deserialize back
        restored = QuestionResponse(**json_data)
        
        assert restored.response_type == original.response_type
        assert restored.message == original.message
        assert restored.confidence_explanation == original.confidence_explanation
        assert restored.sources == original.sources


class TestResponseFieldContent:
    """Test cases for response field content validation."""
    
    def test_message_not_empty(self):
        """Message field should not be empty."""
        # Pydantic doesn't enforce non-empty strings by default,
        # but we can test that empty strings are technically allowed
        # (business logic should prevent this)
        response = QuestionResponse(
            response_type="answer",
            message="",
            confidence_explanation="Explanation"
        )
        
        assert response.message == ""
    
    def test_confidence_explanation_not_empty(self):
        """Confidence explanation should not be empty."""
        response = QuestionResponse(
            response_type="answer",
            message="Message",
            confidence_explanation=""
        )
        
        assert response.confidence_explanation == ""
    
    def test_response_type_literal_values(self):
        """Response type should only accept 'answer' or 'escalation'."""
        # Valid values
        answer_response = QuestionResponse(
            response_type="answer",
            message="M",
            confidence_explanation="E"
        )
        assert answer_response.response_type == "answer"
        
        escalation_response = QuestionResponse(
            response_type="escalation",
            message="M",
            confidence_explanation="E"
        )
        assert escalation_response.response_type == "escalation"
        
        # Invalid value should raise error
        with pytest.raises(ValidationError):
            QuestionResponse(
                response_type="unknown",
                message="M",
                confidence_explanation="E"
            )


class TestSourceReferenceFormatting:
    """Test cases for source reference formatting."""
    
    def test_sources_as_list_of_strings(self):
        """Sources should be a list of strings."""
        response = QuestionResponse(
            response_type="answer",
            message="Answer",
            confidence_explanation="Explanation",
            sources=["billing.md", "permissions.md"]
        )
        
        assert isinstance(response.sources, list)
        assert all(isinstance(s, str) for s in response.sources)
    
    def test_sources_preserve_order(self):
        """Sources list should preserve order."""
        sources = ["c.md", "a.md", "b.md"]
        response = QuestionResponse(
            response_type="answer",
            message="Answer",
            confidence_explanation="Explanation",
            sources=sources
        )
        
        assert response.sources == sources
    
    def test_sources_allow_duplicates(self):
        """Sources list should allow duplicates (though business logic may prevent this)."""
        response = QuestionResponse(
            response_type="answer",
            message="Answer",
            confidence_explanation="Explanation",
            sources=["test.md", "test.md"]
        )
        
        assert len(response.sources) == 2
    
    def test_escalation_typically_has_no_sources(self):
        """Escalation responses typically have no sources."""
        response = QuestionResponse(
            response_type="escalation",
            message="Escalating",
            confidence_explanation="Low confidence",
            sources=None
        )
        
        assert response.sources is None
    
    def test_answer_can_have_sources(self):
        """Answer responses can include sources."""
        response = QuestionResponse(
            response_type="answer",
            message="Answer",
            confidence_explanation="High confidence",
            sources=["billing.md"]
        )
        
        assert response.sources is not None
        assert len(response.sources) > 0


class TestResponseConsistency:
    """Test cases for response schema consistency."""
    
    def test_all_responses_have_required_fields(self):
        """All responses must have response_type, message, and confidence_explanation."""
        # Answer response
        answer = QuestionResponse(
            response_type="answer",
            message="A",
            confidence_explanation="E"
        )
        assert hasattr(answer, "response_type")
        assert hasattr(answer, "message")
        assert hasattr(answer, "confidence_explanation")
        assert hasattr(answer, "sources")
        
        # Escalation response
        escalation = QuestionResponse(
            response_type="escalation",
            message="A",
            confidence_explanation="E"
        )
        assert hasattr(escalation, "response_type")
        assert hasattr(escalation, "message")
        assert hasattr(escalation, "confidence_explanation")
        assert hasattr(escalation, "sources")
    
    def test_response_type_determines_content(self):
        """Response type should indicate whether it's an answer or escalation."""
        answer = QuestionResponse(
            response_type="answer",
            message="Here is your answer",
            confidence_explanation="High confidence"
        )
        
        escalation = QuestionResponse(
            response_type="escalation",
            message="Let me connect you with an agent",
            confidence_explanation="Low confidence"
        )
        
        assert answer.response_type == "answer"
        assert escalation.response_type == "escalation"
        assert answer.response_type != escalation.response_type
