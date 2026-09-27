from google import genai

from app.config import (
    GEMINI_API_KEY,
    GEMINI_TIP_MODEL,
)


def generate_nutrition_tip_with_flash(goal: str):

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add your Gemini API key to the .env file."
        )

    prompt = f"""
You are FitBuddy, a general wellness assistant.

Give ONE concise nutrition or recovery tip
for an adult whose selected goal is:

{goal}

Rules:
- Keep it practical.
- Keep it general wellness advice.
- Do not provide calorie targets.
- Do not recommend fasting.
- Do not prescribe supplements.
- Do not diagnose medical conditions.
- Do not provide medical treatment.
- Mention hydration, balanced meals, sleep,
  or recovery when appropriate.

Return only the tip.
"""

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    response = client.models.generate_content(
        model=GEMINI_TIP_MODEL,
        contents=prompt
    )

    result = (response.text or "").strip()

    if not result:
        raise RuntimeError(
            "Gemini returned an empty nutrition tip."
        )

    return result