import { useState } from 'react'
import './App.css'
import { askQuestion, ApiError } from './services/api'

interface Message {
  role: 'user' | 'assistant';
  content: string;
  confidenceExplanation?: string;
  responseType?: 'answer' | 'escalation';
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    const questionText = input.trim();
    setInput('');
    setLoading(true);

    try {
      const response = await askQuestion(questionText);
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.message,
        confidenceExplanation: response.confidence_explanation,
        responseType: response.response_type
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('API Error:', error);
      
      let errorMessage = 'Sorry, something went wrong. Please try again.';
      
      if (error instanceof ApiError) {
        errorMessage = error.message;
      }
      
      const errorResponse: Message = {
        role: 'assistant',
        content: errorMessage,
        confidenceExplanation: 'Error occurred while processing your request',
        responseType: 'escalation'
      };
      
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>TaskFlow Support Chat</h1>
        <p>Ask questions about TaskFlow features and documentation</p>
      </header>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>Start a conversation by asking a question below</p>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`message ${message.role} ${message.responseType || ''}`}
          >
            <div className="message-content">
              <strong className="message-role">
                {message.role === 'user' ? 'You' : 'Assistant'}
              </strong>
              <p>{message.content}</p>
              
              {message.confidenceExplanation && (
                <div className="confidence-indicator">
                  <span className="confidence-label">Confidence:</span>
                  <span className="confidence-text">{message.confidenceExplanation}</span>
                </div>
              )}
              
              {message.responseType === 'escalation' && (
                <div className="escalation-badge">
                  Escalated to Human Support
                </div>
              )}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="message assistant loading">
            <div className="message-content">
              <strong className="message-role">Assistant</strong>
              <p className="loading-text">Thinking...</p>
            </div>
          </div>
        )}
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          placeholder="Ask a question about TaskFlow..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button 
          type="submit" 
          className="chat-submit"
          disabled={loading || !input.trim()}
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  )
}

export default App
