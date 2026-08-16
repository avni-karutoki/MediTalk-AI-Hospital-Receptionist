import whisper

model = whisper.load_model("small")

result = model.transcribe(
    "audio.m4a",
    fp16=False
)

print(result["text"])