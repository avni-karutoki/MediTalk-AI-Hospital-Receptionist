from agents.extraction_node import extraction_agent


state = {
    "english_text": "I also have fever and cough.",
    "patient_name": "Riddhi",
    "phone": "9876543210",
    "appointment_date": "2026-08-17",
    "appointment_time": "11:00",
    "symptoms": ["back pain", "joint pain"]
}


result = extraction_agent(state)

print(result)