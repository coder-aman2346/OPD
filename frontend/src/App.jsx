/**
 * AI Healthcare Assistant — Main Application
 */
import { useState, useRef, useEffect } from 'react';
import ChatWindow from './components/ChatWindow.jsx';
import MessageInput from './components/MessageInput.jsx';
import MetricsPanel from './components/MetricsPanel.jsx';
import { sendMessage } from './api/client.js';

const WELCOME_CHIPS = [
  "I've been having headaches for a week",
  "I have a persistent ringing in my ears",
  "My back hurts when I sit for too long",
  "I noticed a rash on my arms",
];

export default function App() {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showMetrics, setShowMetrics] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  async function handleSend(text) {
    // Add user message to chat
    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await sendMessage({
        message: text,
        conversationId,
      });

      // Track conversation
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Build assistant message
      const assistantMsg = {
        role: 'assistant',
        content: response.response,
        metrics: response.metrics,
        appointments: response.appointments_created || [],
        piiWarning: response.pii_warning,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, something went wrong. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  function handleNewConversation() {
    setMessages([]);
    setConversationId(null);
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <div className="header-icon">🏥</div>
          <div>
            <div className="header-title">Healthcare Assistant</div>
            <div className="header-subtitle">AI-powered symptom assessment</div>
          </div>
        </div>
        <div className="header-actions">
          <button
            className="btn"
            onClick={() => setShowMetrics(!showMetrics)}
            id="metrics-toggle"
          >
            📊 Metrics
          </button>
          <button
            className="btn btn-primary"
            onClick={handleNewConversation}
            id="new-conversation"
          >
            ＋ New Chat
          </button>
        </div>
      </header>

      {/* Chat Area */}
      <div className="chat-window" id="chat-window">
        {messages.length === 0 ? (
          <div className="welcome">
            <div className="welcome-icon">🩺</div>
            <h2>How can I help you today?</h2>
            <p>
              Describe your symptoms and I'll help you find the right medical
              department and book an appointment.
            </p>
            <div className="welcome-chips">
              {WELCOME_CHIPS.map((chip, i) => (
                <button
                  key={i}
                  className="welcome-chip"
                  onClick={() => handleSend(chip)}
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <ChatWindow messages={messages} isLoading={isLoading} />
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <MessageInput onSend={handleSend} disabled={isLoading} />

      {/* Metrics Panel */}
      {showMetrics && (
        <MetricsPanel onClose={() => setShowMetrics(false)} />
      )}
    </div>
  );
}
