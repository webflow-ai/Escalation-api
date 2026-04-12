"""
Escalation Engine for the Smart Escalation API.

This module provides the EscalationEngine class that:
- Evaluates retrieval quality using relevance scores
- Decides whether to answer or escalate to human agents
- Generates confidence explanations for decisions
- Coordinates LLM calls when answering questions
"""

from typing import List, Literal, Optional
from dataclasses import dataclass

from src.llm_client import LLMClient, LLMResponse
from src.rag import RetrievedChunk


@dataclass
class EscalationDecision:
    """Decision result from the escalation engine."""
    action: Literal["answer", "escalation"]
    message: str
    confidence_explanation: str
    sources: Optional[List[str]] = None


class EscalationEngine:
    """
    Engine that decides whether to answer customer questions or escalate to human agents.
    
    The engine uses multiple signals to make escalation decisions:
    - Relevance scores from retrieval
    - LLM uncertainty signals
    - Coverage diversity of retrieved chunks
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        relevance_threshold: float = 0.5,
        min_chunks_for_answer: int = 1
    ):
        """
        Initialize the escalation engine.
        
        Args:
            llm_client: LLM client for generating answers
            relevance_threshold: Minimum relevance score to consider answering (default: 0.5)
            min_chunks_for_answer: Minimum number of chunks needed to attempt answering
        """
        self.llm_client = llm_client
        self.relevance_threshold = relevance_threshold
        self.min_chunks_for_answer = min_chunks_for_answer
    
    def _should_escalate_based_on_retrieval(
        self,
        retrieved_chunks: List[RetrievedChunk]
    ) -> tuple[bool, str]:
        """
        Determine if escalation is needed based on retrieval quality.
        
        Args:
            retrieved_chunks: Chunks retrieved from RAG system
            
        Returns:
            Tuple of (should_escalate, reason)
        """
        # No chunks retrieved
        if not retrieved_chunks:
            return True, "No relevant information found in help articles"
        
        # Insufficient chunks
        if len(retrieved_chunks) < self.min_chunks_for_answer:
            return True, f"Only {len(retrieved_chunks)} relevant chunk(s) found, insufficient for confident answer"
        
        # Check best relevance score
        max_score = max(chunk.score for chunk in retrieved_chunks)
        if max_score < self.relevance_threshold:
            return True, f"Best retrieval score was {max_score:.2f}, below confidence threshold of {self.relevance_threshold}"
        
        # All checks passed
        return False, ""
    
    def _generate_confidence_explanation(
        self,
        action: Literal["answer", "escalation"],
        retrieved_chunks: List[RetrievedChunk],
        llm_uncertain: bool = False,
        retrieval_reason: str = ""
    ) -> str:
        """
        Generate human-readable confidence explanation.
        
        Args:
            action: Whether answering or escalating
            retrieved_chunks: Retrieved chunks from RAG
            llm_uncertain: Whether LLM signaled uncertainty
            retrieval_reason: Reason for retrieval-based escalation
            
        Returns:
            Confidence explanation string
        """
        if action == "escalation":
            if llm_uncertain:
                return "LLM indicated uncertainty in answering based on available context"
            elif retrieval_reason:
                return retrieval_reason
            else:
                return "Insufficient confidence to provide accurate answer"
        
        # For answers, provide positive confidence signal
        if not retrieved_chunks:
            return "Answer generated with available context"
        
        max_score = max(chunk.score for chunk in retrieved_chunks)
        sources = list(set(chunk.source for chunk in retrieved_chunks))
        
        if len(sources) == 1:
            return f"High confidence - retrieved relevant content from '{sources[0]}' with similarity score {max_score:.2f}"
        else:
            return f"High confidence - retrieved relevant content from {len(sources)} help articles with best similarity score {max_score:.2f}"
    
    def _extract_sources(self, retrieved_chunks: List[RetrievedChunk]) -> List[str]:
        """
        Extract unique source article names from retrieved chunks.
        
        Args:
            retrieved_chunks: Retrieved chunks from RAG
            
        Returns:
            List of unique source filenames
        """
        if not retrieved_chunks:
            return []
        
        sources = list(set(chunk.source for chunk in retrieved_chunks))
        return sorted(sources)
    
    def process_question(
        self,
        question: str,
        retrieved_chunks: List[RetrievedChunk]
    ) -> EscalationDecision:
        """
        Process a customer question and decide whether to answer or escalate.
        
        This is the main entry point for the escalation engine. It:
        1. Evaluates retrieval quality
        2. If quality is sufficient, calls LLM to generate answer
        3. Checks LLM response for uncertainty signals
        4. Returns decision with confidence explanation
        
        Args:
            question: Customer question
            retrieved_chunks: Retrieved chunks from RAG system
            
        Returns:
            EscalationDecision with action, message, and explanation
            
        Example:
            >>> engine = EscalationEngine(llm_client)
            >>> decision = engine.process_question("How do I reset password?", chunks)
            >>> decision.action
            'answer'
            >>> decision.message
            'To reset your password, go to...'
        """
        # First check: Should we escalate based on retrieval quality?
        should_escalate, retrieval_reason = self._should_escalate_based_on_retrieval(
            retrieved_chunks
        )
        
        if should_escalate:
            # Escalate due to poor retrieval
            return EscalationDecision(
                action="escalation",
                message="I'm not certain I can answer this accurately. Let me connect you with a human support agent who can help.",
                confidence_explanation=self._generate_confidence_explanation(
                    action="escalation",
                    retrieved_chunks=retrieved_chunks,
                    retrieval_reason=retrieval_reason
                ),
                sources=None
            )
        
        # Retrieval quality is sufficient, attempt to generate answer
        try:
            # Extract chunk contents for LLM
            chunk_contents = [chunk.content for chunk in retrieved_chunks]
            
            # Generate answer using LLM
            llm_response: LLMResponse = self.llm_client.generate_answer(
                question=question,
                context_chunks=chunk_contents
            )
            
            # Second check: Did LLM signal uncertainty?
            if llm_response.uncertain:
                # Escalate due to LLM uncertainty
                return EscalationDecision(
                    action="escalation",
                    message="I'm not certain I can answer this accurately. Let me connect you with a human support agent who can help.",
                    confidence_explanation=self._generate_confidence_explanation(
                        action="escalation",
                        retrieved_chunks=retrieved_chunks,
                        llm_uncertain=True
                    ),
                    sources=None
                )
            
            # All checks passed - return answer
            return EscalationDecision(
                action="answer",
                message=llm_response.answer,
                confidence_explanation=self._generate_confidence_explanation(
                    action="answer",
                    retrieved_chunks=retrieved_chunks
                ),
                sources=self._extract_sources(retrieved_chunks)
            )
            
        except Exception as e:
            # If LLM call fails, escalate gracefully
            error_msg = str(e)
            
            # Log the actual error for debugging
            print(f"ERROR in escalation engine: {error_msg}")
            import traceback
            traceback.print_exc()
            
            # Provide specific error context in explanation
            if "timeout" in error_msg.lower():
                explanation = "Unable to generate response due to timeout, escalating to human agent"
            elif "rate limit" in error_msg.lower():
                explanation = "Service temporarily busy, escalating to human agent"
            else:
                explanation = f"Unable to generate response, escalating to human agent (Error: {error_msg})"
            
            return EscalationDecision(
                action="escalation",
                message="I'm having trouble processing your question right now. Let me connect you with a human support agent who can help.",
                confidence_explanation=explanation,
                sources=None
            )
