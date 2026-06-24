/**
 * Chat message display with appointment cards and metrics.
 */
import AppointmentCard from './AppointmentCard.jsx';
import MetricsBadge from './MetricsBadge.jsx';

export default function ChatWindow({ messages, isLoading }) {
  return (
    <>
      {messages.map((msg, index) => (
        <div key={index}>
          {/* PII Warning */}
          {msg.piiWarning && (
            <div className="pii-warning">
              <span>⚠️</span>
              <span>{msg.piiWarning}</span>
            </div>
          )}

          {/* Message Bubble */}
          <div className={`message message-${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🏥'}
            </div>
            <div>
              <div className="message-content">
                {msg.content.split('\n').map((line, i) => (
                  <span key={i}>
                    {line}
                    {i < msg.content.split('\n').length - 1 && <br />}
                  </span>
                ))}
              </div>

              {/* Metrics Badge (assistant messages only) */}
              {msg.role === 'assistant' && msg.metrics && (
                <MetricsBadge metrics={msg.metrics} />
              )}
            </div>
          </div>

          {/* Appointment Cards */}
          {msg.appointments && msg.appointments.length > 0 && (
            msg.appointments.map((apt, aptIdx) => (
              <AppointmentCard key={aptIdx} appointment={apt} />
            ))
          )}
        </div>
      ))}

      {/* Typing Indicator */}
      {isLoading && (
        <div className="typing-indicator">
          <div className="message-avatar" style={{
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-light)',
            width: 32,
            height: 32,
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 16,
          }}>
            🏥
          </div>
          <div className="typing-dots">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        </div>
      )}
    </>
  );
}
