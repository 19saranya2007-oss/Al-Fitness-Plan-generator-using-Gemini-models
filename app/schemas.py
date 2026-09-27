from typing import Literal

from pydantic import BaseModel, Field, field_validator


class UserInput(BaseModel):
    username: str = Field(
        min_length=2,
        max_length=80
    )

    user_id: str = Field(
        min_length=2,
        max_length=50
    )

    age: int = Field(
        ge=18,
        le=100
    )

    weight_kg: float = Field(
        gt=20,
        lt=400
    )

    goal: Literal[
        "general wellness",
        "flexibility",
        "fitness"
    ]

    intensity: Literal[
        "low",
        "medium",
        "high"
    ]

    @field_validator("username", "user_id")
    @classmethod
    def clean_text(cls, value: str):
        return " ".join(
            value.strip().split()
        )


class FeedbackRequest(BaseModel):
    user_id: str = Field(
        min_length=2,
        max_length=50
    )

    feedback: str = Field(
        min_length=3,
        max_length=1000
    )

    @field_validator("user_id", "feedback")
    @classmethod
    def clean_feedback_text(cls, value: str):
        return value.strip()