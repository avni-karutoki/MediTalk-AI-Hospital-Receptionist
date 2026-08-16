from agents.registration_agent import registration_agent

state = {
    "patient_name": "Rahul Sharma",
    "phone": "+919876543210",
    "age": 25,
    "gender": "Male",
    "preferred_language": "Hindi"
}

result = registration_agent(state)

print(result)