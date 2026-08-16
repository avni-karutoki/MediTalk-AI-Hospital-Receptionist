from strapi_service import (
    find_patient,
    create_patient
)


def registration_agent(state):
    """
    Identify an existing patient using their phone number.

    Collect complete registration information only when the
    patient does not already exist in Strapi.
    """

    # Patient was already identified or created during
    # an earlier conversation turn.
    if (
        state.get("patient_id")
        and state.get("patient_document_id")
    ):
        return state

    patient_name = state.get(
        "patient_name"
    )

    phone = state.get(
        "phone"
    )

    age = state.get(
        "age"
    )

    gender = state.get(
        "gender"
    )

    insurance = state.get(
        "insurance"
    )

    address = state.get(
        "address"
    )

    language = (
        state.get("preferred_language")
        or (
            "Hindi"
            if state.get(
                "conversation_language"
            ) == "hi"
            else "English"
        )
    )

    # -------------------------
    # Basic identification
    # -------------------------

    if not patient_name:
        state["needs_input"] = (
            "patient_name"
        )

        state["message"] = (
            "Please tell me your name."
        )

        return state

    if not phone:
        state["needs_input"] = "phone"

        state["message"] = (
            "Please tell me your phone number "
            "so I can identify or register you."
        )

        return state

    # -------------------------
    # Search existing patient
    # -------------------------

    patient = find_patient(
        phone
    )

    if patient:
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

        state["patient_id"] = (
            patient["id"]
        )

        state["patient_document_id"] = (
            patient["documentId"]
        )

        state["patient_name"] = (
            patient.get("name")
            or patient_name
        )

        state["registration_status"] = (
            "Existing Patient"
        )

        state["returning_patient"] = True

        return state

    # -------------------------
    # New-patient information
    # -------------------------

    if age is None:
        state["needs_input"] = "age"

        state["message"] = (
            "Please tell me your age."
        )

        return state

    try:
        age = int(age)

        if age <= 0 or age > 120:
            state["needs_input"] = "age"

            state["message"] = (
                "Please provide a valid age "
                "between 1 and 120."
            )

            return state

    except (TypeError, ValueError):
        state["needs_input"] = "age"

        state["message"] = (
            "Please tell me your age as a number."
        )

        return state

    if not gender:
        state["needs_input"] = "gender"

        state["message"] = (
            "Please tell me your gender."
        )

        return state

    if not insurance:
        state["needs_input"] = "insurance"

        state["message"] = (
            "Please tell me whether you have "
            "health insurance. You may also say "
            "that you do not have insurance."
        )

        return state

    if not address:
        state["needs_input"] = "address"

        state["message"] = (
            "Please tell me your address."
        )

        return state

    # All mandatory new-patient details are available.
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

    # IMPORTANT:
    # Insaurance and Address use the same spelling and
    # capitalization as your current Strapi field identifiers.
    new_patient = create_patient({
        "name": patient_name,
        "phone": phone,
        "age": age,
        "gender": gender,
        "preferred_language": language,
        "Insaurance": insurance,
        "Address": address
    })

    if new_patient:
        state["patient_id"] = (
            new_patient["id"]
        )

        state["patient_document_id"] = (
            new_patient["documentId"]
        )

        state["registration_status"] = (
            "New Patient Created"
        )

        state["returning_patient"] = False

    else:
        state["error"] = (
            "Patient registration failed"
        )

        state["message"] = (
            "I could not complete your "
            "registration. Please try again."
        )

    return state