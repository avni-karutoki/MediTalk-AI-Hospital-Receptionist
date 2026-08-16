import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def translation_node(state):
    spoken_text = state.get("spoken_text", "")

    if not spoken_text:
        state["english_text"] = ""
        return state

    prompt = f"""
Translate the following patient's speech into clear, natural English.

The speech may be Hindi, Hinglish, another Indian language,
or a regional dialect.

IMPORTANT:
- Preserve ALL information from the original speech.
- Pay special attention to dates and relative dates.
- Translate "कल" as "tomorrow" when it means the next day.
- Translate "परसों" as "day after tomorrow".
- Translate "आज" as "today".
- Do not omit words that indicate date, time, name, phone number,
  symptoms, or appointment intent.
- If the speech is grammatically unclear or contains speech-recognition
  mistakes, infer the most likely meaning from the surrounding words,
  but do not invent new information.
- Do not give medical advice.
- Do not diagnose anything.
- Return only the English translation.

Patient's speech:
{spoken_text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        state["english_text"] = response.text.strip()

    except Exception as e:
        state["english_text"] = spoken_text
        state["translation_error"] = str(e)

    return state