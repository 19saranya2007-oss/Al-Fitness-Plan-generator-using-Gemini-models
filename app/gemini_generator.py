from google import genai

from app.config import (
    GEMINI_API_KEY,
    GEMINI_WORKOUT_MODEL,
)


DISCLAIMER = (
    "This is general wellness information, not medical advice. "
    "Stop an exercise if it causes pain and consult a qualified "
    "professional for health or injury concerns."
)


def get_gemini_client():

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add your Gemini API key to the .env file."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


def generate_workout_gemini(
    username: str,
    age: int,
    goal: str,
    intensity: str
):

    prompt = f"""
You are FitBuddy, an AI wellness planning assistant.

Create a personalized 7-day general wellness activity plan.

USER INFORMATION

Name:
{username}

Age:
{age}

Goal:
{goal}

Preferred intensity:
{intensity}


REQUIREMENTS

1. Create exactly 7 days.
2. Clearly label Day 1 through Day 7.
3. Include a warm-up.
4. Include the main workout or activity.
5. Include approximate duration.
6. Include cooldown or recovery.
7. Include suitable rest or recovery.
8. Make the plan practical and easy to understand.
9. Consider the requested intensity.
10. Do not diagnose medical conditions.
11. Do not prescribe medication.
12. Do not prescribe supplements.
13. Do not prescribe calorie restriction.
14. Do not recommend fasting.
15. Do not promise a specific physical result.

At the end include this safety message:

{DISCLAIMER}
"""

    client = get_gemini_client()

    response = client.models.generate_content(
        model=GEMINI_WORKOUT_MODEL,
        contents=prompt
    )

    result = (response.text or "").strip()

    if not result:
        raise RuntimeError(
            "Gemini returned an empty workout plan."
        )

    return result