import whisper

model = whisper.load_model("small")


def voice_node(state):
    audio_path = state.get("audio_path")

    if not audio_path:
        state["error"] = "No audio file provided"
        return state

    try:
        result = model.transcribe(
            audio_path,
            fp16=False,
            temperature=0
        )

        state["spoken_text"] = result["text"].strip()
        state["detected_language"] = result["language"]

    except Exception as e:
        state["error"] = str(e)

    return state