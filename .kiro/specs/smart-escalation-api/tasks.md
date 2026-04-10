# Implementation Plan: Smart Escalation API

## Overview

This implementation plan follows a 4-phase approach to build a RAG-based customer support system with intelligent escalation. The system uses FastAPI, FAISS vector store, sentence-transformers embeddings, and an LLM API to answer customer questions about TaskFlow or escalate to human agents when uncertain.

**Total Estimated Time**: 2-3.5 hours

**Key Focus**: Escalation logic is the most critical component. Property-based testing ensures correctness of core behaviors.

## Tasks

### Phase 1: Core RAG System (1 hour)

- [x] 1. Set up project structure and dependencies
  - Create project directory structure (`data/articles/`, `src/`, `tests/`)
  - Create `requirements.txt` with FastAPI, FAISS, sentence-transformers, pytest, hypothesis
  - Create `.env.example` file with required environment variables
  - Create `README.md` with setup instructions
  - _Requirements: 10.4_

- [x] 2. Create help article knowledge base
  - [x] 2.1 Write 5 TaskFlow help articles as markdown files
    - Create `data/articles/getting-started.md` (TaskFlow basics, account setup, first project)
    - Create `data/articles/billing.md` (subscription plans, payment methods, billing cycles)
    - Create `data/articles/integrations.md` (Slack, GitHub, Jira integrations)
    - Create `data/articles/permissions.md` (team roles, access control, admin settings)
    - Create `data/articles/troubleshooting.md` (common errors, login issues, performance tips)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [x] 3. Implement article chunking logic
  - [x] 3.1 Create `src/chunking.py` with text chunking function
    - Implement fixed-size chunking with overlap (500 chars, 50 char overlap)
    - Preserve sentence boundaries where possible
    - Track source article metadata for each chunk
    - _Requirements: 2.2, 2.6_
  
  - [x] 3.2 Write property test for chunking semantic coherence
    - **Property 3: Chunking Semantic Coherence**
    - **Validates: Requirements 2.6**
    - Test that chunks don't split words mid-character
    - Test that overlap is maintained between consecutive chunks
    - Use Hypothesis to generate random article texts

- [x] 4. Implement RAG system with FAISS vector store
  - [x] 4.1 Create `src/rag.py` with RAGSystem class
    - Implement article loading from `data/articles/` directory
    - Initialize sentence-transformers embedding model (all-MiniLM-L6-v2)
    - Generate embeddings for all chunks
    - Build in-memory FAISS index
    - Implement `retrieve()` method for similarity search
    - _Requirements: 2.1, 2.3, 2.4, 2.5_
  
  - [ ]* 4.2 Write property test for top-k retrieval behavior
    - **Property 2: Top-K Retrieval Behavior**
    - **Validates: Requirements 2.4**
    - Test that retrieval returns exactly k chunks (or fewer if total < k)
    - Test that chunks are ordered by descending relevance score
    - Use Hypothesis to generate different k values

- [x] 5. Checkpoint - Test RAG system with sample questions
  - Ensure RAG system loads articles and retrieves relevant chunks, ask the user if questions arise.

### Phase 2: API and Escalation Logic (1 hour)

- [x] 6. Implement LLM client
  - [x] 6.1 Create `src/llm_client.py` with LLMClient class
    - Implement Google Gemini API integration
    - Create prompt template with customer support instructions
    - Implement `generate_answer()` method
    - Parse LLM responses for uncertainty signals
    - Add error handling for API timeouts and rate limits
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_
  
  - [ ]* 6.2 Write property test for prompt construction completeness
    - **Property 6: Prompt Construction Completeness**
    - **Validates: Requirements 9.4, 9.5**
    - Test that constructed prompts include complete question text
    - Test that all retrieved chunk contents are included in prompt
    - Use Hypothesis to generate random questions and chunk lists

- [x] 7. Implement escalation engine
  - [x] 7.1 Create `src/escalation.py` with EscalationEngine class
    - Implement relevance threshold checking (default 0.5)
    - Implement escalation decision logic
    - Generate confidence explanations for answers and escalations
    - Coordinate LLM calls when answering
    - _Requirements: 3.5, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 7.2 Write property test for escalation on low confidence
    - **Property 4: Escalation on Low Confidence**
    - **Validates: Requirements 3.5, 4.2, 4.4**
    - Test that escalation occurs when max relevance score < threshold
    - Test that escalation occurs when LLM signals uncertainty
    - Use Hypothesis to generate relevance scores below threshold

- [x] 8. Create FastAPI application
  - [x] 8.1 Create `src/main.py` with FastAPI app
    - Define Pydantic models (QuestionRequest, QuestionResponse)
    - Implement POST `/ask` endpoint
    - Configure CORS for frontend access
    - Wire together RAG system, escalation engine, and LLM client
    - Add request validation and error handling
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 8.2 Write property test for invalid request handling
    - **Property 1: Invalid Request Handling**
    - **Validates: Requirements 1.4**
    - Test that malformed requests return 400 status code
    - Test that missing required fields return error messages
    - Use Hypothesis to generate invalid request payloads
  
  - [ ]* 8.3 Write property test for response schema consistency
    - **Property 5: Response Schema Consistency**
    - **Validates: Requirements 5.1, 6.1, 6.2, 6.3, 6.4, 6.5**
    - Test that all responses conform to JSON schema
    - Test that response_type is either "answer" or "escalation"
    - Test that required fields have correct types
    - Use Hypothesis to generate random valid questions

- [x] 9. Implement configuration management
  - [x] 9.1 Create `src/config.py` with Pydantic settings
    - Define Settings class with environment variables
    - Set default values for thresholds and parameters
    - Load configuration from `.env` file
    - _Requirements: 10.5_

- [x] 10. Checkpoint - Test API end-to-end
  - Ensure API accepts questions and returns valid responses, ask the user if questions arise.

### Phase 3: Frontend (0.5-1 hour)

- [ ] 11. Set up React frontend with Vite
  - [ ] 11.1 Create React project structure
    - Initialize Vite project with React and TypeScript
    - Install dependencies (axios for API calls)
    - Create `frontend/.env.example` with API URL
    - _Requirements: 7.5_

- [ ] 12. Implement chat interface
  - [ ] 12.1 Create ChatInterface component
    - Implement message state management (user and assistant messages)
    - Create text input field for customer questions
    - Create submit button with loading state
    - Display chat history with user questions and API responses
    - Show confidence explanations for each response
    - Differentiate between answer and escalation response types
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.6_
  
  - [ ]* 12.2 Write unit tests for ChatInterface component
    - Test that user questions appear in chat history
    - Test loading state during API calls
    - Test display of API responses
    - Use React Testing Library and Vitest

- [ ] 13. Integrate frontend with backend API
  - [ ] 13.1 Implement API client
    - Create API service function to POST questions to `/ask` endpoint
    - Handle API errors gracefully
    - Configure CORS and API URL from environment variables
    - _Requirements: 1.3_

- [ ] 14. Add basic styling
  - [ ] 14.1 Style chat interface
    - Add minimal CSS for chat layout
    - Style message bubbles (user vs assistant)
    - Add loading indicator
    - Ensure mobile responsiveness
    - _Requirements: 7.5_

### Phase 4: Testing and Deployment (0.5 hour)

- [ ] 15. Write unit tests for core components
  - [ ]* 15.1 Write unit tests for chunking logic
    - Test chunk size and overlap calculations
    - Test sentence boundary preservation
    - _Requirements: 2.2, 2.6_
  
  - [ ]* 15.2 Write unit tests for escalation decision rules
    - Test threshold comparisons
    - Test confidence explanation generation
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 15.3 Write unit tests for response formatting
    - Test JSON construction
    - Test source reference inclusion
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 16. Write integration tests
  - [ ]* 16.1 Test end-to-end API flow
    - Test answerable questions return answer responses
    - Test out-of-scope questions trigger escalation
    - Mock LLM API responses
    - _Requirements: 1.1, 1.2_
  
  - [ ]* 16.2 Test error handling
    - Test LLM API timeout handling
    - Test invalid API key handling
    - Test network error handling
    - _Requirements: 1.4_
  
  - [ ]* 16.3 Test CORS configuration
    - Verify CORS headers are present
    - Test OPTIONS requests
    - _Requirements: 1.3_

- [ ] 17. Create deployment documentation
  - [ ] 17.1 Update README with deployment instructions
    - Document Render/Railway deployment steps for backend
    - Document Vercel deployment steps for frontend
    - Include environment variable configuration
    - Add troubleshooting section
    - _Requirements: 1.5, 10.4_

- [ ] 18. Deploy to hosting platforms
  - [ ] 18.1 Deploy backend to Render or Railway
    - Create web service
    - Configure build and start commands
    - Set environment variables (API keys, thresholds)
    - Verify deployment and test with sample requests
    - _Requirements: 1.5_
  
  - [ ] 18.2 Deploy frontend to Vercel
    - Create new project
    - Configure build settings
    - Set API URL environment variable
    - Verify deployment and test chat interface
    - _Requirements: 1.5, 7.5_

- [ ] 19. Final checkpoint - End-to-end testing
  - Test deployed application with various question types (in-scope, out-of-scope, edge cases), verify LLM responses have appropriate tone, check confidence explanations are helpful, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate the 6 correctness properties defined in the design
- Unit tests validate specific examples and edge cases
- Checkpoints ensure incremental validation at key milestones
- Focus on escalation logic as the most critical component
- Use Python for backend (FastAPI, FAISS, sentence-transformers)
- Use TypeScript for frontend (React, Vite)
