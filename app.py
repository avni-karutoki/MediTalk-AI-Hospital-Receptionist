from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import os
import shutil
import uuid

from graph import graph
from agents.response_translation_agent import translate_response


app = FastAPI(
    title="AI Hospital Receptionist"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Temporary in-memory conversation storage.
sessions = {}


UPLOAD_DIR = "audio"
os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


ALLOWED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".mpeg",
    ".mp4",
    ".webm"
}


SUPPORTED_CONVERSATION_LANGUAGES = {
    "hi",
    "en"
}


def prepare_localized_response(result):
    """
    Preserve the patient's original conversation language and
    translate the receptionist's response into that language.

    The conversation language is selected during the first turn
    and preserved for later turns.

    This prevents a phone-number-only response from changing a
    Hindi conversation into English.
    """

    conversation_language = result.get(
        "conversation_language"
    )

    # Select the language only once.
    if not conversation_language:
        detected_language = result.get(
            "detected_language",
            "en"
        )

        if (
            detected_language
            not in SUPPORTED_CONVERSATION_LANGUAGES
        ):
            detected_language = "en"

        conversation_language = detected_language

    result["conversation_language"] = (
        conversation_language
    )

    # The message may be a follow-up question or
    # the final confirmation.
    original_message = (
        result.get("response")
        or result.get("message")
    )

    localized_message = translate_response(
        original_message,
        conversation_language
    )

    result["localized_message"] = (
        localized_message
    )

    return result


@app.post("/reception")
async def receptionist(
    session_id: str,
    audio: UploadFile = File(...)
):
    # -------------------------
    # Validate session ID
    # -------------------------

    if not session_id or not session_id.strip():
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "response_language": "en",
                "message": (
                    "A valid session ID is required."
                )
            }
        )

    # -------------------------
    # Validate uploaded audio
    # -------------------------

    if not audio.filename:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "session_id": session_id,
                "response_language": "en",
                "message": (
                    "Please upload an audio file."
                )
            }
        )

    original_filename = os.path.basename(
        audio.filename
    )

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "session_id": session_id,
                "response_language": "en",
                "message": (
                    "Unsupported audio format. "
                    "Please upload a WAV, MP3, M4A, "
                    "MP4, MPEG or WebM audio file."
                )
            }
        )

    # Generate a unique filename so separate audio
    # uploads cannot overwrite each other.
    safe_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    audio_path = os.path.join(
        UPLOAD_DIR,
        safe_filename
    )

    # -------------------------
    # Save uploaded audio
    # -------------------------

    try:
        with open(
            audio_path,
            "wb"
        ) as buffer:
            shutil.copyfileobj(
                audio.file,
                buffer
            )

    except Exception as error:
        print(
            f"Audio upload failed: {error}"
        )

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "session_id": session_id,
                "response_language": "en",
                "message": (
                    "The audio file could not "
                    "be processed."
                )
            }
        )

    # Reject an empty audio file.
    if (
        not os.path.exists(audio_path)
        or os.path.getsize(audio_path) == 0
    ):
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "session_id": session_id,
                "response_language": "en",
                "message": (
                    "The uploaded audio file is empty."
                )
            }
        )

    # -------------------------
    # Restore conversation
    # -------------------------

    if session_id in sessions:
        state = sessions[session_id]

        # Only replace the audio path.
        # Preserve conversation_language and all
        # accumulated patient information.
        state["audio_path"] = audio_path

    else:
        state = {
            "audio_path": audio_path
        }

    print(
        "STATE BEFORE GRAPH:",
        state
    )

    # -------------------------
    # Run LangGraph safely
    # -------------------------

    try:
        result = graph.invoke(state)

        # Translate the receptionist response into
        # the patient's original language.
        result = prepare_localized_response(
            result
        )

    except Exception as error:
        print(
            f"Reception graph failed: {error}"
        )

        saved_language = state.get(
            "conversation_language",
            "en"
        )

        error_message = (
            "I could not process your request. "
            "Please start again."
        )

        localized_error = translate_response(
            error_message,
            saved_language
        )

        sessions.pop(
            session_id,
            None
        )

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "session_id": session_id,
                "response_language": saved_language,
                "message": localized_error
            }
        )

    # -------------------------
    # Handle agent errors
    # -------------------------

    if result.get("error"):
        print(
            f"Agent error: {result['error']}"
        )

        sessions.pop(
            session_id,
            None
        )

        fallback_message = (
            "The appointment could not be "
            "completed. Please try again."
        )

        message = (
            result.get("localized_message")
            or translate_response(
                fallback_message,
                result.get(
                    "conversation_language",
                    "en"
                )
            )
        )

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "session_id": session_id,
                "response_language": result.get(
                    "conversation_language",
                    "en"
                ),
                "message": message
            }
        )

    # -------------------------
    # Missing patient information
    # -------------------------

    if result.get("needs_input"):
        # Save the complete state, including the
        # original conversation language.
        sessions[session_id] = result

        return {
            "status": "needs_input",
            "session_id": session_id,
            "needs_input": result["needs_input"],

            "response_language": result.get(
                "conversation_language",
                "en"
            ),

            "message": (
                result.get("localized_message")
                or result.get("message")
            )
        }

    # -------------------------
    # Completed conversation
    # -------------------------

    sessions.pop(
        session_id,
        None
    )

    return {
        "status": "completed",
        "session_id": session_id,

        "patient_name": result.get(
            "patient_name"
        ),

        "patient_id": result.get(
            "patient_id"
        ),

        "department": result.get(
            "department"
        ),

        "urgency": result.get(
            "urgency"
        ),

        "symptoms": result.get(
            "symptoms"
        ),

        "doctor": result.get(
            "doctor"
        ),

        "doctor_id": result.get(
            "doctor_id"
        ),

        "appointment_id": result.get(
            "appointment_id"
        ),

        "appointment_date": result.get(
            "appointment_date"
        ),

        "appointment_time": result.get(
            "appointment_time"
        ),

        "appointment_status": result.get(
            "appointment_status"
        ),

        "returning_patient": result.get(
            "returning_patient"
        ),

        "registration_status": result.get(
            "registration_status"
        ),

        "history": result.get(
            "history"
        ),

        "sms_status": result.get(
            "sms_status"
        ),

        "sms_id": result.get(
            "sms_id"
        ),

        # Tell the UI which voice to use.
        "response_language": result.get(
            "conversation_language",
            "en"
        ),

        # Return translated text for both display
        # and browser speech synthesis.
        "message": (
            result.get("localized_message")
            or result.get("response")
            or result.get("message")
        )
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": (
            "AI Hospital Receptionist"
        )
    }