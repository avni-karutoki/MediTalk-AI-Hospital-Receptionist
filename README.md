# MediTalk — AI Hospital Receptionist

MediTalk is a multilingual,voice-first AI hospital receptionist that helps patients register with a hospital and book doctor appointments through natural conversation.

The system is designed for patients who may not understand English, have limited technical knowledge, or find traditional hospital registration screens difficult to use.

Patients can speak naturally in Hindi or English. MediTalk transcribes their speech, understands their details and symptoms, identifies the appropriate department, registers new patients, finds an available doctor and automatically books an appointment.

## Problem Statement

Patients frequently face long queues at hospital reception counters for registration and appointment booking.

Traditional hospital kiosks and registration screens may also be inaccessible to:

- Patients who do not understand English
- Elderly patients
- Patients with limited technical knowledge
- Patients who cannot comfortably use digital interfaces
- People who prefer speaking in their native language

MediTalk replaces form-based interaction with a simple voice conversation.

## Solution Overview

MediTalk provides an Alexa-like hospital reception experience.

A patient can speak in Hindi or English to:

- Register as a new patient
- Be identified as a returning patient
- Provide age, gender, address and insurance information
- Explain symptoms conversationally
- Select an appointment date
- Get routed to the appropriate hospital department
- Receive an automatically assigned doctor and available time slot
- Book an appointment in the hospital’s Strapi backend
- Hear the receptionist’s response in the same language used by the patient

## Core Features

- Voice-first hospital reception
- Hindi and Indian English support
- Local Whisper speech-to-text
- Same-language spoken responses
- Multi-turn conversational memory
- New-patient registration
- Returning-patient identification using phone number
- Age, gender, address and insurance collection
- Symptom extraction across multiple conversation turns
- Duplicate-free symptom merging
- AI-assisted medical department routing
- Urgency classification
- Doctor selection based on availability
- Automatic available-time assignment
- Appointment creation in Strapi
- Patient appointment-history retrieval
- FastAPI REST endpoint
- Alexa-style MediTalk voice interface
- Audio upload and live microphone recording
- Processing indicator and session reset
- Basic audio and workflow error handling

## Technology Stack

### AI and Agent Orchestration

- OpenAI Whisper — local speech-to-text
- Google Gemini — translation, extraction and triage
- LangGraph — multi-agent workflow orchestration
- Browser Speech Synthesis — multilingual voice responses

### Backend

- Python
- FastAPI
- REST API
- In-memory conversational sessions

### Hospital Data Layer

- Strapi
- Strapi REST API
- SQLite
- Patients, doctors, departments and appointments collections

### Frontend

- React
- TypeScript
- Vinext/Vite
- HTML and CSS
- MediaRecorder API
- Web Speech Synthesis API

## Technical Workflow

```text
Patient speaks in Hindi or English
              ↓
Microphone records patient audio
              ↓
FastAPI receives the audio file
              ↓
Whisper transcribes the speech
              ↓
Language detection
              ↓
Gemini translates speech into English for internal processing
              ↓
Extraction agent collects:
name, phone, age, gender, insurance, address,
symptoms, appointment date and language
              ↓
LangGraph preserves information across conversation turns
              ↓
Triage agent determines:
department, urgency and confidence
              ↓
Registration agent searches Strapi using phone number
              ↓
Existing patient OR new-patient registration
              ↓
Memory agent retrieves previous appointment history
              ↓
Appointment agent finds an available doctor
              ↓
Doctor's available time is automatically selected
              ↓
Appointment is created in Strapi
              ↓
Confirmation is translated into the patient's language
              ↓
MediTalk displays and speaks the confirmation
