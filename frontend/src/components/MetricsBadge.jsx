/**
 * Per-response metrics badge showing token usage and latency.
 */
export default function MetricsBadge({ metrics }) {
  if (!metrics) return null;

  return (
    <div className="metrics-badge">
      <div className="metrics-badge-item">
        <span>⚡</span>
        <span className="metrics-badge-value">{metrics.latency_ms}ms</span>
      </div>
      <div className="metrics-badge-item">
        <span>📥</span>
        <span className="metrics-badge-value">{metrics.input_tokens}</span>
      </div>
      <div className="metrics-badge-item">
        <span>📤</span>
        <span className="metrics-badge-value">{metrics.output_tokens}</span>
      </div>
      <div className="metrics-badge-item">
        <span>📊</span>
        <span className="metrics-badge-value">{metrics.total_tokens} tok</span>
      </div>
      {metrics.model && (
        <div className="metrics-badge-item">
          <span>🤖</span>
          <span className="metrics-badge-value">{metrics.model}</span>
        </div>
      )}
    </div>
  );
}
