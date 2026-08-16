from agents.voice_node import voice_node


state = {
    "audio_path": "audio/audio.m4a"
}

updated_state = voice_node(state)

print(updated_state)