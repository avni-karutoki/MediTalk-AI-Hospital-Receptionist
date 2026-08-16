import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

try:
    from twilio.rest import Client
    twilio_client = Client(TWILIO_SID, TWILIO_TOKEN) if TWILIO_SID and TWILIO_TOKEN else None
except Exception:
    twilio_client = None


def notification_agent(state):

    patient_name = state.get("patient_name", "Patient")
    phone = state.get("phone")
    doctor = state.get("doctor")
    department = state.get("department")
    date = state.get("appointment_date")
    time = state.get("appointment_time")
    fee = state.get("consultation_fee")

    message = (
        f"Hospital Appointment Confirmation\n\n"
        f"Patient: {patient_name}\n"
        f"Doctor: {doctor}\n"
        f"Department: {department}\n"
        f"Date: {date}\n"
        f"Time: {time}\n"
        f"Consultation Fee: ₹{fee}\n\n"
        f"Please arrive 15 minutes early.\n"
        f"Thank you."
    )

    state["response"] = message

    if twilio_client and phone and TWILIO_PHONE:
        try:
            sms = twilio_client.messages.create(
                body=message,
                from_=TWILIO_PHONE,
                to=phone
            )

            state["sms_status"] = "sent"
            state["sms_id"] = sms.sid

        except Exception as e:
            state["sms_status"] = "failed"
            state["sms_error"] = str(e)

    else:
        state["sms_status"] = "mock_sent"
        state["sms_id"] = "MOCK_SMS_001"

    return state