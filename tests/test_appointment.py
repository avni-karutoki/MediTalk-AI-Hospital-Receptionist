from agents.appointment_agent import appointment_agent

state = {
    "patient_name": "Riddhi",
    "phone": None,
    "department": "General Medicine",
    "appointment_date": "2026-08-17",
    "appointment_time": None,
    "symptoms": [],
    "urgency": "Low"
}

result = appointment_agent(state)

print(result)