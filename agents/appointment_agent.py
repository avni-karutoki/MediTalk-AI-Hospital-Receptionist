from datetime import datetime

from strapi_service import (
    get_doctors,
    create_appointment
)


def select_best_doctor(
    doctors,
    appointment_date
):
    """
    Select a doctor who is available on the
    requested appointment day.

    Fall back to the first doctor if no exact
    availability match is found.
    """

    try:
        day_name = datetime.strptime(
            appointment_date,
            "%Y-%m-%d"
        ).strftime("%A")

    except (ValueError, TypeError):
        return doctors[0]

    available_doctors = [
        doctor
        for doctor in doctors
        if day_name in doctor.get(
            "available_days",
            []
        )
    ]

    if available_doctors:
        available_doctors.sort(
            key=lambda doctor: doctor.get(
                "available_time",
                "99:99"
            )
        )

        return available_doctors[0]

    return doctors[0]


def clean_symptoms(symptoms):
    """
    Convert symptoms into a clean,
    duplicate-free list.
    """

    if not symptoms:
        return []

    if isinstance(symptoms, str):
        symptoms = [symptoms]

    if not isinstance(symptoms, list):
        return []

    cleaned_symptoms = []

    for symptom in symptoms:
        if not symptom:
            continue

        symptom = str(
            symptom
        ).strip().lower()

        if (
            symptom
            and symptom not in cleaned_symptoms
        ):
            cleaned_symptoms.append(
                symptom
            )

    return cleaned_symptoms


def appointment_agent(state):
    department = state.get(
        "department"
    )

    patient_id = state.get(
        "patient_id"
    )

    patient_document_id = state.get(
        "patient_document_id"
    )

    appointment_date = state.get(
        "appointment_date"
    )

    appointment_time = state.get(
        "appointment_time"
    )

    symptoms = clean_symptoms(
        state.get("symptoms", [])
    )

    state["symptoms"] = symptoms

    # -------------------------
    # Validate patient
    # -------------------------

    if (
        not patient_id
        or not patient_document_id
    ):
        state["error"] = (
            "Patient registration is incomplete"
        )

        state["message"] = (
            "I could not complete your registration. "
            "Please start again."
        )

        return state

    # -------------------------
    # Ask for symptoms
    # -------------------------

    if not symptoms:
        state["needs_input"] = "symptoms"

        state["message"] = (
            "Please tell me what symptoms "
            "you are experiencing."
        )

        return state

    # -------------------------
    # Ask for appointment date
    # -------------------------

    if not appointment_date:
        state["needs_input"] = (
            "appointment_date"
        )

        state["message"] = (
            "What date would you like "
            "for the appointment?"
        )

        return state

    # -------------------------
    # Ask for appointment time
    # -------------------------

    if not appointment_time:
        state["needs_input"] = (
            "appointment_time"
        )

        state["message"] = (
            "What time would you like "
            "for the appointment?"
        )

        return state

    # All required appointment information
    # has now been collected.
    state.pop(
        "needs_input",
        None
    )

    state.pop(
        "message",
        None
    )

    state.pop(
        "error",
        None
    )

    print(
        "APPOINTMENT SYMPTOMS:",
        symptoms
    )

    # -------------------------
    # Get available doctors
    # -------------------------

    doctors = get_doctors(
        department
    )

    if not doctors:
        state["error"] = (
            f"No doctors available in {department}"
        )

        state["message"] = (
            "No doctor is currently available "
            "for this department. Please try again."
        )

        return state

    selected_doctor = select_best_doctor(
        doctors,
        appointment_date
    )

    # -------------------------
    # Create appointment
    # -------------------------

    appointment = create_appointment({
        "patient_id": patient_id,

        "patient_document_id": (
            patient_document_id
        ),

        "doctor_document_id": (
            selected_doctor["documentId"]
        ),

        "appointment_date": (
            appointment_date
        ),

        "appointment_time": (
            appointment_time
        ),

        "symptoms": symptoms
    })

    if not appointment:
        state["error"] = (
            "Failed to create appointment"
        )

        state["message"] = (
            "The appointment could not be "
            "created. Please try again."
        )

        return state

    # -------------------------
    # Save appointment details
    # -------------------------

    state["doctor"] = (
        selected_doctor["name"]
    )

    state["doctor_id"] = (
        selected_doctor["id"]
    )

    state["doctor_available_days"] = (
        selected_doctor.get(
            "available_days",
            []
        )
    )

    state["doctor_available_time"] = (
        selected_doctor.get(
            "available_time"
        )
    )

    state["consultation_fee"] = (
        selected_doctor.get(
            "consultation_fee"
        )
    )

    state["appointment_id"] = (
        appointment["id"]
    )

    state["appointment_status"] = (
        appointment.get(
            "appointment_status",
            "Confirmed"
        )
    )

    return state