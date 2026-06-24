/**
 * API client for the Healthcare Assistant backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Send a chat message to the assistant.
 */
export async function sendMessage({ message, conversationId, patientName }) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      conversation_id: conversationId || null,
      patient_name: patientName || null,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Chat request failed: ${error}`);
  }

  return response.json();
}

/**
 * Fetch all appointments.
 */
export async function fetchAppointments(conversationId) {
  const params = conversationId ? `?conversation_id=${conversationId}` : '';
  const response = await fetch(`${API_BASE}/appointments${params}`);

  if (!response.ok) {
    throw new Error('Failed to fetch appointments');
  }

  return response.json();
}

/**
 * Fetch aggregate metrics.
 */
export async function fetchMetrics() {
  const response = await fetch(`${API_BASE}/metrics`);

  if (!response.ok) {
    throw new Error('Failed to fetch metrics');
  }

  return response.json();
}
