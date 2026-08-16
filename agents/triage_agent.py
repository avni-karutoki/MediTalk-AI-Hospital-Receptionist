import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


EMERGENCY_KEYWORDS = [
    "chest pain",
    "difficulty breathing",
    "shortness of breath",
    "unconscious",
    "severe bleeding",
    "stroke",
    "heart attack",
    "seizure"
]


DEPARTMENT_FALLBACK = {
    "chest pain": "Cardiology",
    "difficulty breathing": "Cardiology",
    "shortness of breath": "Cardiology",
    "back pain": "Orthopedics",
    "joint pain": "Orthopedics",
    "fracture": "Orthopedics",
    "fever": "General Medicine",
    "cough": "General Medicine",
    "headache": "General Medicine",
    "pregnancy": "Gynecology",
    "pregnancy checkup": "Gynecology",
    "irregular periods": "Gynecology"
}


def merge_symptoms(existing_symptoms, new_symptoms):
    """
    Merge symptoms without duplicates while preserving their order.

    Example:
    ["fever"] + ["headache"] -> ["fever", "headache"]
    """

    merged = []

    for symptom in existing_symptoms + new_symptoms:
        if not isinstance(symptom, str):
            continue

        symptom = symptom.strip().lower()

        if symptom and symptom not in merged:
            merged.append(symptom)

    return merged


def triage_agent(state):
    """
    Determine department and urgency while preserving the symptoms
    already collected by the extraction agent.
    """

    text = state.get("english_text", "")
    lower_text = text.lower()

    # The extraction agent owns this symptom list.
    existing_symptoms = state.get("symptoms", [])

    if not isinstance(existing_symptoms, list):
        existing_symptoms = []

    existing_symptoms = merge_symptoms(existing_symptoms, [])

    # Search both the current statement and accumulated symptoms
    # for deterministic emergency keywords.
    complete_symptom_text = " ".join(existing_symptoms).lower()
    emergency_search_text = f"{lower_text} {complete_symptom_text}"

    detected_emergency_symptoms = [
        keyword
        for keyword in EMERGENCY_KEYWORDS
        if keyword in emergency_search_text
    ]

    # Emergency keywords are deterministic, so they may safely be
    # preserved if the extraction model missed one.
    if detected_emergency_symptoms:
        state["symptoms"] = merge_symptoms(
            existing_symptoms,
            detected_emergency_symptoms
        )

        state["department"] = "Cardiology"
        state["urgency"] = "High"
        state["triage_confidence"] = 0.99
        state["emergency_case"] = True

        return state

    prompt = f"""
You are a hospital triage assistant.

Determine the most appropriate hospital department and urgency using
the accumulated symptoms.

Current patient statement:
{text}

Accumulated symptoms:
{json.dumps(existing_symptoms)}

Return ONLY valid JSON in this format:

{{
  "department": "Cardiology | Orthopedics | General Medicine | Gynecology",
  "urgency": "High | Medium | Low",
  "confidence": 0.0
}}

Rules:
- Use only the accumulated symptoms provided above.
- Do not extract, invent, add, remove, rename, or modify symptoms.
- The extraction agent has already completed symptom extraction.
- Choose exactly one department.
- High = emergency.
- Medium = should see a doctor soon.
- Low = routine consultation.
- Confidence must be between 0 and 1.
- Return JSON only.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        result = json.loads(response.text)

        # Critical fix:
        # Triage preserves the extraction agent's symptom list exactly.
        # It does not read or merge Gemini-generated symptoms.
        state["symptoms"] = existing_symptoms

        state["department"] = result.get(
            "department",
            "General Medicine"
        )

        state["urgency"] = result.get(
            "urgency",
            "Medium"
        )

        state["triage_confidence"] = result.get(
            "confidence",
            0.8
        )

        state["emergency_case"] = (
            str(state["urgency"]).lower() == "high"
        )

    except Exception as error:
        # Even if Gemini fails, preserve the symptoms exactly.
        state["symptoms"] = existing_symptoms

        fallback_search_text = (
            f"{lower_text} {' '.join(existing_symptoms).lower()}"
        )

        department = "General Medicine"

        for symptom, mapped_department in DEPARTMENT_FALLBACK.items():
            if symptom in fallback_search_text:
                department = mapped_department
                break

        state["department"] = department
        state["urgency"] = "Medium"
        state["triage_confidence"] = 0.5
        state["emergency_case"] = False

        print(f"Triage Gemini error; fallback used: {error}")

    return state