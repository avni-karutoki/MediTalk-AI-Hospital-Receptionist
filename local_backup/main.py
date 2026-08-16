from fastapi import FastAPI
from graph import graph

app = FastAPI(title="AI Hospital Receptionist")

@app.get("/")
def home():
    return {"message": "AI Hospital Receptionist Backend Running"}

@app.post("/voice-chat")
def voice_chat():

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

    return result