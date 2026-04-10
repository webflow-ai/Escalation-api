"""
LLM Client for generating customer support responses using Google Gemini API.

This module provides the LLMClient class that handles:
- Google Gemini API integration
- Prompt construction with customer support instructions
- Response generation with uncertainty detection
- Error handling for API timeouts and rate limits
"""

import os
import time
from typing import List, Optional
from dataclasses import dataclass

import google.generativeai as genai


@dataclass
class LLMResponse:
    """Response from LLM generation."""
    answer: str
    uncertain: bool  # True if LLM signals uncertainty


class LLMClient:
    """Client for interacting with Google Gemini API to generate support responses."""
    
    # Uncertainty signals that indicate the LLM is not confident
    UNCERTAINTY_SIGNALS = [
        "i'm not certain",
        "i'm not sure",
        "i don't have enough information",
        "let me connect you with",
        "human agent",
        "i cannot answer",
        "i'm unable to",
        "not enough information",
        "outside my knowledge",
        "i don't know"
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.3,
        max_retries: int = 2,
        timeout: int = 30
    ):
        """
        Initialize LLM client with Google Gemini API.
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model_name: Gemini model to use
            temperature: Sampling temperature (0.0-1.0, lower = more deterministic)
            max_retries: Maximum number of retry attempts for failed requests
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not provided. Set GOOGLE_API_KEY environment variable.")
        
        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": self.temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
    
    def build_prompt(self, question: str, context_chunks: List[str]) -> str:
        """
        Build prompt with customer support instructions and context.
        
        Args:
            question: Customer question
            context_chunks: Retrieved help article chunks
            
        Returns:
            Formatted prompt string
        """
        # Format context chunks
        context_text = "\n\n".join([
            f"[Context {i+1}]\n{chunk}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        prompt = f"""You are a friendly customer support agent for TaskFlow, a project management SaaS.

Answer the customer's question using ONLY the information provided in the help articles below.

IMPORTANT RULES:
- Use a friendly, helpful tone
- Ground your answer in the provided context
- If the context doesn't contain enough information to answer confidently, respond with: "I'm not certain about this. Let me connect you with a human agent."
- Do not make up or infer information not present in the context
- Be concise and direct in your response

HELP ARTICLE CONTEXT:
{context_text}

CUSTOMER QUESTION:
{question}

YOUR ANSWER:"""
        
        return prompt
    
    def _detect_uncertainty(self, response_text: str) -> bool:
        """
        Detect if LLM response contains uncertainty signals.
        
        Args:
            response_text: Generated response text
            
        Returns:
            True if uncertainty detected, False otherwise
        """
        response_lower = response_text.lower()
        return any(signal in response_lower for signal in self.UNCERTAINTY_SIGNALS)
    
    def generate_answer(
        self,
        question: str,
        context_chunks: List[str]
    ) -> LLMResponse:
        """
        Generate answer using LLM with retrieved context.
        
        Args:
            question: Customer question
            context_chunks: Retrieved help article chunks
            
        Returns:
            LLMResponse with answer text and uncertainty flag
            
        Raises:
            ValueError: If question or context is empty
            RuntimeError: If API call fails after retries
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        if not context_chunks:
            raise ValueError("Context chunks cannot be empty")
        
        # Build the prompt
        prompt = self.build_prompt(question, context_chunks)
        
        # Attempt generation with retries
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                # Generate response
                response = self.model.generate_content(
                    prompt,
                    request_options={"timeout": self.timeout}
                )
                
                # Extract text from response
                if not response.text:
                    # Empty response indicates uncertainty
                    return LLMResponse(
                        answer="I'm not certain about this. Let me connect you with a human agent.",
                        uncertain=True
                    )
                
                answer_text = response.text.strip()
                
                # Detect uncertainty in response
                uncertain = self._detect_uncertainty(answer_text)
                
                return LLMResponse(
                    answer=answer_text,
                    uncertain=uncertain
                )
                
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                # Check for rate limiting
                if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg:
                    if attempt < self.max_retries:
                        # Exponential backoff for rate limits
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RuntimeError(
                            "Rate limit exceeded. Please try again later."
                        ) from e
                
                # Check for timeout
                if "timeout" in error_msg:
                    if attempt < self.max_retries:
                        continue
                    else:
                        raise RuntimeError(
                            "Request timed out. Please try again."
                        ) from e
                
                # Check for invalid API key
                if "api key" in error_msg or "authentication" in error_msg or "401" in error_msg:
                    raise RuntimeError(
                        "Invalid API key. Please check your configuration."
                    ) from e
                
                # For other errors, retry if attempts remain
                if attempt < self.max_retries:
                    time.sleep(1)
                    continue
                else:
                    raise RuntimeError(
                        f"Failed to generate response: {str(e)}"
                    ) from e
        
        # Should not reach here, but handle gracefully
        raise RuntimeError(
            f"Failed to generate response after {self.max_retries + 1} attempts: {str(last_error)}"
        )
