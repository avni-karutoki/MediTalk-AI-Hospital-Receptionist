import os
import json

from datetime import datetime

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def clean_symptoms(symptoms):
    """
    Convert symptoms into a clean, duplicate-free list.
    """

    if not symptoms:
        return []

    if isinstance(symptoms, str):
        symptoms = [symptoms]

    if not isinstance(symptoms, list):
        return []

    cleaned = []

    for symptom in symptoms:
        if not symptom:
            continue

        symptom = str(
            symptom
        ).strip().lower()

        if symptom and symptom not in cleaned:
            cleaned.append(symptom)

    return cleaned


def extraction_agent(state):
    english_text = state.get(
        "english_text",
        ""
    )

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    prompt = f"""
Extract patient registration, symptoms and appointment information
from the following patient speech.

Today's date is {today}.

Return ONLY valid JSON with exactly these fields:

{{
    "patient_name": null,
    "phone": null,
    "age": null,
    "gender": null,
    "insurance": null,
    "address": null,
    "appointment_date": null,
    "appointment_time": null,
    "preferred_language": null,
    "symptoms": []
}}

Rules:

PATIENT NAME:
- Extract the patient's name only when mentioned.
- Do not invent a name.
- If not mentioned, return null.

PHONE:
- Extract the patient's phone number when mentioned.
- Return only the digits as a string.
- Remove spaces, commas and hyphens.
- Indian phone numbers normally contain 10 digits.
- If not mentioned, return null.

AGE:
- Extract the patient's age when explicitly mentioned.
- Return age as a number, not a string.
- Examples:
  "I am 24 years old" means 24.
  "मेरी उम्र 24 साल है" means 24.
- Do not calculate age unless the patient explicitly gives it.
- If age is not mentioned, return null.

GENDER:
- Extract gender only when explicitly mentioned.
- Normalize the value to one of:
  "Male"
  "Female"
  "Other"
- If not mentioned, return null.

INSURANCE:
- Extract the patient's insurance information when mentioned.
- Preserve the insurer or scheme name.
- Examples:
  "Ayushman Bharat"
  "Star Health"
  "CGHS"
  "No insurance"
- If the patient says they do not have insurance,
  return "No insurance".
- If insurance is not discussed, return null.

ADDRESS:
- Extract the patient's address when mentioned.
- Preserve area, city and other address information.
- Do not invent missing parts.
- If not mentioned, return null.

APPOINTMENT DATE:
- Convert relative dates into YYYY-MM-DD.
- "today" means today's date.
- "tomorrow" means one day after today.
- "day after tomorrow" means two days after today.
- Understand natural Indian English and common Indian speech patterns.
- If no date is mentioned, return null.

APPOINTMENT TIME:
- Extract the appointment time when mentioned.
- Understand:
  "11 AM"
  "11:30 AM"
  "at 2"
  "2 PM"
  "सुबह 11 बजे"
- Return time in HH:MM 24-hour format.
- If no time is mentioned, return null.

PREFERRED LANGUAGE:
- Extract the preferred language only when the patient explicitly
  provides it.
- Examples: "Hindi", "English".
- If not mentioned, return null.

SYMPTOMS:
- Extract every symptom explicitly mentioned by the patient.
- Return symptoms as a JSON array.
- Use short symptom names.
- Do not diagnose the patient.
- Do not convert symptoms into diseases.
- Do not add symptoms that were not mentioned.
- If no symptoms are mentioned, return [].

Example:

"My name is Riddhi, I am 20 years old and I have fever"

Return:

{{
    "patient_name": "Riddhi",
    "phone": null,
    "age": 20,
    "gender": null,
    "insurance": null,
    "address": null,
    "appointment_date": null,
    "appointment_time": null,
    "preferred_language": null,
    "symptoms": ["fever"]
}}

Example:

"I am female and I have Ayushman Bharat insurance"

Return:

{{
    "patient_name": null,
    "phone": null,
    "age": null,
    "gender": "Female",
    "insurance": "Ayushman Bharat",
    "address": null,
    "appointment_date": null,
    "appointment_time": null,
    "preferred_language": null,
    "symptoms": []
}}

If a value is not present, return null.
Do not invent information.
Do not provide medical advice.
Return only valid JSON.

Patient speech:

{english_text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        response_text = response.text.strip()

        if response_text.startswith("```"):
            response_text = (
                response_text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        extracted = json.loads(
            response_text
        )

        print(
            "EXTRACTION RESULT:",
            extracted
        )

        # Never overwrite information collected during
        # an earlier turn with None.
        fields_to_merge = [
            "patient_name",
            "phone",
            "age",
            "gender",
            "insurance",
            "address",
            "appointment_date",
            "appointment_time",
            "preferred_language"
        ]

        for field in fields_to_merge:
            value = extracted.get(field)

            if value is not None and value != "":
                state[field] = value

        # Merge symptoms across conversation turns.
        existing_symptoms = clean_symptoms(
            state.get("symptoms", [])
        )

        new_symptoms = clean_symptoms(
            extracted.get("symptoms", [])
        )

        for symptom in new_symptoms:
            if symptom not in existing_symptoms:
                existing_symptoms.append(
                    symptom
                )

        state["symptoms"] = (
            existing_symptoms
        )

        print(
            "MERGED SYMPTOMS:",
            state["symptoms"]
        )

        return state

    except Exception as error:
        print(
            f"Extraction error: {error}"
        )

        state["error"] = (
            "Patient information extraction failed"
        )

        state["message"] = (
            "I could not understand that response. "
            "Please say it again."
        )

        return state