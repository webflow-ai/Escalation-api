/**
 * API client for Smart Escalation API
 * Handles communication with the backend /ask endpoint
 */

// API Response Types
export interface ApiResponse {
  response_type: 'answer' | 'escalation';
  message: string;
  confidence_explanation: string;
  sources: string[] | null;
}

// API Request Types
export interface QuestionRequest {
  question: string;
}

// Error Types
export class ApiError extends Error {
  statusCode?: number;
  originalError?: unknown;

  constructor(
    message: string,
    statusCode?: number,
    originalError?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.originalError = originalError;
  }
}

/**
 * Get API URL from environment variables
 * For Vercel deployment, uses relative path /api
 * For local development, uses localhost:8000
 */
const getApiUrl = (): string => {
  // In production (Vercel), use relative path to serverless function
  // In development, use environment variable or default to localhost
  return import.meta.env.VITE_API_URL || '/api';
};

/**
 * POST a question to the API endpoint
 * 
 * @param question - The customer question to submit
 * @returns Promise resolving to the API response
 * @throws ApiError on network errors, timeouts, or invalid responses
 */
export const askQuestion = async (question: string): Promise<ApiResponse> => {
  const apiUrl = getApiUrl();
  const endpoint = apiUrl; // Use /api directly (not /api/ask)

  // Validate input
  if (!question || question.trim().length === 0) {
    throw new ApiError('Question cannot be empty', 400);
  }

  const requestBody: QuestionRequest = {
    question: question.trim()
  };

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Handle HTTP errors
    if (!response.ok) {
      let errorMessage = `API request failed with status ${response.status}`;
      
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // If error response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }

      throw new ApiError(errorMessage, response.status);
    }

    // Parse response
    const data = await response.json();

    // Validate response structure
    if (!isValidApiResponse(data)) {
      throw new ApiError('Invalid response format from API', 500);
    }

    return data;

  } catch (error) {
    // Handle network errors
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new ApiError('Request timeout - please try again', 408, error);
      }
      
      if (error.message.includes('fetch')) {
        throw new ApiError(
          'Unable to connect to the API. Please check your connection and try again.',
          0,
          error
        );
      }

      throw new ApiError(
        `Network error: ${error.message}`,
        0,
        error
      );
    }

    throw new ApiError('An unexpected error occurred', 0, error);
  }
};

/**
 * Type guard to validate API response structure
 */
function isValidApiResponse(data: unknown): data is ApiResponse {
  if (typeof data !== 'object' || data === null) {
    return false;
  }

  const response = data as Record<string, unknown>;

  return (
    typeof response.response_type === 'string' &&
    (response.response_type === 'answer' || response.response_type === 'escalation') &&
    typeof response.message === 'string' &&
    typeof response.confidence_explanation === 'string' &&
    (response.sources === null || Array.isArray(response.sources))
  );
}
