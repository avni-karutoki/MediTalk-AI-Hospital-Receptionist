from agents.voice_node import voice_node
from agents.translation_node import translation_node
from agents.extraction_node import extraction_agent


state = {
    "audio_path":"audio/patient.mpeg"
}


state = voice_node(state)

print("\nVOICE:")
print(state)

state = translation_node(state)

print("\nTRANSLATION:")
print(state)

state = extraction_agent(state)

print("\nEXTRACTION:")
print(state)