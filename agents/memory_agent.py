from strapi_service import get_patient_history


def memory_agent(state):

    patient_document_id = state.get("patient_document_id")

    if not patient_document_id:
        state["returning_patient"] = False
        return state

    history = get_patient_history(patient_document_id)

    if history:
        state["returning_patient"] = True
        state["history"] = history
    else:
        state["returning_patient"] = False

    return state