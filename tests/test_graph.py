from graph import graph

state = {
    "audio_path": "audio/audio.m4a",
    "patient_name": "Rahul Sharma",
    "phone": "+919876543210",
    "age": 25,
    "gender": "Male",
    "preferred_language": "Hindi",
    "appointment_date": "15 Aug 2026",
    "appointment_time": "10:00 AM"
}

result = graph.invoke(state)

print(result)