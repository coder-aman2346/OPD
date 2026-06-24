/**
 * Metrics side panel showing aggregate application metrics.
 */
import { useState, useEffect } from 'react';
import { fetchMetrics } from '../api/client.js';

export default function MetricsPanel({ onClose }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMetrics();
    const interval = setInterval(loadMetrics, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  async function loadMetrics() {
    try {
      const data = await fetchMetrics();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load metrics:', err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="metrics-panel">
      <div className="metrics-panel-header">
        <h3 className="metrics-panel-title">📊 Observability</h3>
        <button className="metrics-close" onClick={onClose}>✕</button>
      </div>

      {loading && <p style={{ color: 'var(--text-muted)' }}>Loading metrics...</p>}

      {metrics && (
        <div className="metrics-grid">
          <div className="metrics-card">
            <div className="metrics-card-label">Total Requests</div>
            <div className="metrics-card-value">{metrics.total_requests}</div>
          </div>
          <div className="metrics-card">
            <div className="metrics-card-label">Appointments</div>
            <div className="metrics-card-value">{metrics.total_appointments}</div>
          </div>
          <div className="metrics-card">
            <div className="metrics-card-label">Avg Latency</div>
            <div className="metrics-card-value">{metrics.avg_latency_ms}ms</div>
          </div>
          <div className="metrics-card">
            <div className="metrics-card-label">Avg TTFT</div>
            <div className="metrics-card-value">{metrics.avg_ttft_ms}ms</div>
          </div>
          <div className="metrics-card">
            <div className="metrics-card-label">Input Tokens</div>
            <div className="metrics-card-value">{metrics.total_input_tokens.toLocaleString()}</div>
          </div>
          <div className="metrics-card">
            <div className="metrics-card-label">Output Tokens</div>
            <div className="metrics-card-value">{metrics.total_output_tokens.toLocaleString()}</div>
          </div>
          <div className="metrics-card">
            <div className="metrics-card-label">Cached Tokens</div>
            <div className="metrics-card-value">{metrics.total_cached_tokens.toLocaleString()}</div>
          </div>
          <div className="metrics-card">
            <div className="metrics-card-label">Total Tokens</div>
            <div className="metrics-card-value">{metrics.total_tokens.toLocaleString()}</div>
          </div>
          <div className="metrics-card metrics-card-full">
            <div className="metrics-card-label">Estimated Cost</div>
            <div className="metrics-card-value">${metrics.total_cost_usd.toFixed(4)}</div>
          </div>
        </div>
      )}
    </div>
  );
}
