from google import genai

from app.config import (
    GEMINI_API_KEY,
    GEMINI_WORKOUT_MODEL,
)

from app.gemini_generator import DISCLAIMER


def update_workout_plan(
    original_plan: str,
    feedback: str,
    goal: str,
    intensity: str
):
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add your Gemini API key to the .env file."
        )

    prompt = f"""
You are FitBuddy.

Update an existing 7-day general wellness activity plan
based on user feedback.

GOAL:
{goal}

INTENSITY:
{intensity}

ORIGINAL PLAN:
----------------
{original_plan}
----------------

USER FEEDBACK:
----------------
{feedback}
----------------

RULES:

1. Keep the 7-day structure.
2. Apply the user's feedback where reasonable.
3. Keep the plan safe and practical.
4. Include recovery days or recovery activities where appropriate.
5. Do not diagnose medical conditions.
6. Do not prescribe medication.
7. Do not prescribe supplements.
8. Do not prescribe calorie restriction.
9. Do not recommend fasting.
10. Do not promise a specific physical result.

Finish with:

{DISCLAIMER}
"""

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    response = client.models.generate_content(
        model=GEMINI_WORKOUT_MODEL,
        contents=prompt
    )

    result = (response.text or "").strip()

    if not result:
        raise RuntimeError(
            "Gemini returned an empty updated plan."
        )

    return result