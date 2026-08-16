import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


LANGUAGE_NAMES = {
    "hi": "Hindi",
    "en": "English"
}


def translate_response(message, language_code):
    """
    Translate the receptionist's response back into the
    language selected at the beginning of the conversation.
    """

    if not message:
        return message

    # No translation is required for English.
    if language_code == "en":
        return message

    language_name = LANGUAGE_NAMES.get(
        language_code,
        "English"
    )

    prompt = f"""
You are translating a hospital receptionist's response.

Translate the following response into natural, respectful and
easy-to-understand {language_name}.

Rules:
- Preserve patient names exactly.
- Preserve doctor names exactly.
- Preserve dates, times, phone numbers and currency amounts exactly.
- Use simple conversational language.
- Do not add medical advice.
- Do not add explanations.
- Return only the translated response.

Receptionist response:
{message}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        translated_message = response.text.strip()

        if translated_message:
            return translated_message

    except Exception as error:
        print(
            f"Response translation failed: {error}"
        )

    # Return the original response if translation fails.
    return message