from langgraph.graph import StateGraph, START, END

from agents.voice_node import voice_node
from agents.translation_node import translation_node
from agents.extraction_node import extraction_agent
from agents.triage_agent import triage_agent
from agents.registration_agent import registration_agent
from agents.memory_agent import memory_agent
from agents.appointment_agent import appointment_agent
from agents.notification_agent import notification_agent

def appointment_router(state):
    if state.get("error"):
        return "error"

    if state.get("needs_input"):
        return "wait"

    return "continue"
def registration_router(state):
    if state.get("error"):
        return "error"

    registration_fields = {
        "patient_name",
        "phone",
        "age",
        "gender",
        "insurance",
        "address"
    }

    if state.get("needs_input") in registration_fields:
        return "wait"

    return "continue"

builder = StateGraph(dict)


builder.add_node("voice", voice_node)
builder.add_node("translate", translation_node)
builder.add_node("extract", extraction_agent)
builder.add_node("triage", triage_agent)
builder.add_node("registration", registration_agent)
builder.add_node("memory", memory_agent)
builder.add_node("appointment", appointment_agent)
builder.add_node("notification", notification_agent)


builder.add_edge(START, "voice")
builder.add_edge("voice", "translate")
builder.add_edge("translate", "extract")
builder.add_edge("extract", "triage")
builder.add_edge("triage", "registration")
builder.add_conditional_edges(
    "registration",
    registration_router,
    {
        "wait": END,
        "error": END,
        "continue": "memory"
    }
)
builder.add_edge("memory", "appointment")
builder.add_conditional_edges(
    "appointment",
    appointment_router,
    {
        "error": END,
        "wait": END,
        "continue": "notification"
    }
)
builder.add_edge("notification", END)


graph = builder.compile()