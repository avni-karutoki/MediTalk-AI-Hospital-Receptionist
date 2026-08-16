from agents.notification_agent import notification_agent

state = {
    "patient_name": "Anjali Verma",
    "phone": "+919812345678",
    "doctor": "Dr. Amit Gupta",
    "department": "Orthopedics",
    "appointment_date": "2026-08-18",
    "appointment_time": "11:00 AM",
    "consultation_fee": 700
}

result = notification_agent(state)

print(result)