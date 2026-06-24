/**
 * Appointment card component shown inline when appointments are created.
 */
export default function AppointmentCard({ appointment }) {
  return (
    <div className="appointment-card">
      <div className="appointment-card-header">
        <span>✅</span>
        <span>Appointment Booked</span>
      </div>
      <div className="appointment-card-body">
        <div className="appointment-field">
          <div className="appointment-field-label">Patient</div>
          <div className="appointment-field-value">{appointment.patient_name}</div>
        </div>
        <div className="appointment-field">
          <div className="appointment-field-label">Department</div>
          <div className="appointment-field-value">{appointment.department}</div>
        </div>
        <div className="appointment-field">
          <div className="appointment-field-label">Visit Date</div>
          <div className="appointment-field-value">{appointment.visit_date}</div>
        </div>
        <div className="appointment-field">
          <div className="appointment-field-label">Appointment ID</div>
          <div className="appointment-field-value" style={{ fontSize: '11px', fontFamily: 'monospace' }}>
            {appointment.appointment_id.slice(0, 8)}...
          </div>
        </div>
        {appointment.summary && (
          <div className="appointment-field appointment-summary">
            <div className="appointment-field-label">Doctor Summary</div>
            <div className="appointment-field-value" style={{ fontWeight: 400, lineHeight: 1.5 }}>
              {appointment.summary}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
