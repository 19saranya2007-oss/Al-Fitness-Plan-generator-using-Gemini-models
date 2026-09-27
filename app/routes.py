from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import (
    get_all_users,
    get_user,
    save_plan,
    save_user,
    update_plan,
)

from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan

from app.schemas import FeedbackRequest, UserInput


# IMPORTANT
router = APIRouter()


BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@router.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None
        }
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight_kg: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):

    try:

        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight_kg=weight_kg,
            goal=goal,
            intensity=intensity
        )

        workout_plan = generate_workout_gemini(
            username=data.username,
            age=data.age,
            goal=data.goal,
            intensity=data.intensity
        )

        nutrition_tip = generate_nutrition_tip_with_flash(
            data.goal
        )

        save_user(
            user_id=data.user_id,
            username=data.username,
            age=data.age,
            weight_kg=data.weight_kg,
            goal=data.goal,
            intensity=data.intensity
        )

        save_plan(
            user_id=data.user_id,
            plan=workout_plan,
            nutrition_tip=nutrition_tip
        )

        user = get_user(data.user_id)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "workout_plan": workout_plan,
                "nutrition_tip": nutrition_tip,
                "message": "Your 7-day plan has been generated.",
                "error": None
            }
        )

    except Exception as error:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(error)
            },
            status_code=400
        )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...)
):

    try:

        feedback_data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback
        )

        user = get_user(
            feedback_data.user_id
        )

        if not user:
            raise ValueError(
                "User ID not found. Generate a plan first."
            )

        updated_plan = update_workout_plan(
            original_plan=user.original_plan,
            feedback=feedback_data.feedback,
            goal=user.goal,
            intensity=user.intensity
        )

        nutrition_tip = generate_nutrition_tip_with_flash(
            user.goal
        )

        update_plan(
            user_id=feedback_data.user_id,
            updated_plan=updated_plan,
            feedback=feedback_data.feedback,
            nutrition_tip=nutrition_tip
        )

        updated_user = get_user(
            feedback_data.user_id
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": updated_user,
                "workout_plan": updated_plan,
                "nutrition_tip": nutrition_tip,
                "message": "Plan updated successfully using your feedback.",
                "error": None
            }
        )

    except Exception as error:

        user = get_user(user_id)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "workout_plan": "",
                "nutrition_tip": "",
                "message": None,
                "error": str(error)
            },
            status_code=400
        )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(request: Request):

    users = get_all_users()

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users
        }
    )


@router.get("/api/users")
def api_users():

    users = get_all_users()

    return [
        {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight_kg": user.weight_kg,
            "goal": user.goal,
            "intensity": user.intensity,
            "has_updated_plan": bool(
                user.updated_plan
            )
        }
        for user in users
    ]


@router.get("/api/users/{user_id}")
def api_user(user_id: str):

    user = get_user(user_id)

    if not user:
        return {
            "error": "User not found"
        }

    return {
        "user_id": user.user_id,
        "username": user.username,
        "age": user.age,
        "weight_kg": user.weight_kg,
        "goal": user.goal,
        "intensity": user.intensity,
        "original_plan": user.original_plan,
        "updated_plan": user.updated_plan,
        "nutrition_tip": user.nutrition_tip,
        "feedback": user.feedback
    }