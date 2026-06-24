"""Prompt templates for generating conversation summaries."""

SUMMARY_PROMPT = """Summarize the following conversation between a patient and an AI healthcare assistant. 
Create a concise summary that captures:
- The patient's symptoms and complaints
- Duration and severity of symptoms
- Any follow-up information provided
- Departments recommended
- Appointments booked (if any)
- Any outstanding questions or concerns

Keep the summary under 200 words. This summary will be used as context for continuing the conversation.

Conversation:
{conversation}
"""

DOCTOR_SUMMARY_PROMPT = """Based on the following patient conversation, generate a concise doctor-facing clinical summary.

Format:
- Chief Complaint: [primary symptom]
- Duration: [how long]
- Severity: [scale or description]
- Associated Symptoms: [related symptoms]
- Patient-Reported History: [any relevant history mentioned]
- Recommended Department: {department}

Keep it professional and concise. Use medical terminology where appropriate.

Conversation:
{conversation}
"""
