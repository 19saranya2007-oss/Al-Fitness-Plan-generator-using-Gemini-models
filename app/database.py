from typing import Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[str] = mapped_column(
        unique=True,
        index=True
    )

    username: Mapped[str]
    age: Mapped[int]
    weight_kg: Mapped[float]
    goal: Mapped[str]
    intensity: Mapped[str]

    original_plan: Mapped[str] = mapped_column(
        default=""
    )

    updated_plan: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )

    nutrition_tip: Mapped[str] = mapped_column(
        default=""
    )

    feedback: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )


# Database connection
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# IMPORTANT: This function is required by main.py
def init_db():
    Base.metadata.create_all(bind=engine)


def save_user(
    user_id: str,
    username: str,
    age: int,
    weight_kg: float,
    goal: str,
    intensity: str
):
    with SessionLocal() as db:

        existing_user = db.scalar(
            select(User).where(
                User.user_id == user_id
            )
        )

        if existing_user:

            existing_user.username = username
            existing_user.age = age
            existing_user.weight_kg = weight_kg
            existing_user.goal = goal
            existing_user.intensity = intensity

            db.commit()
            db.refresh(existing_user)

            return existing_user

        user = User(
            user_id=user_id,
            username=username,
            age=age,
            weight_kg=weight_kg,
            goal=goal,
            intensity=intensity
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user


def save_plan(
    user_id: str,
    plan: str,
    nutrition_tip: str
):
    with SessionLocal() as db:

        user = db.scalar(
            select(User).where(
                User.user_id == user_id
            )
        )

        if not user:
            raise ValueError("User not found")

        user.original_plan = plan
        user.nutrition_tip = nutrition_tip
        user.updated_plan = None
        user.feedback = None

        db.commit()


def update_plan(
    user_id: str,
    updated_plan: str,
    feedback: str,
    nutrition_tip: str
):
    with SessionLocal() as db:

        user = db.scalar(
            select(User).where(
                User.user_id == user_id
            )
        )

        if not user:
            raise ValueError("User not found")

        user.updated_plan = updated_plan
        user.feedback = feedback
        user.nutrition_tip = nutrition_tip

        db.commit()


def get_user(user_id: str):

    with SessionLocal() as db:

        return db.scalar(
            select(User).where(
                User.user_id == user_id
            )
        )


def get_all_users():

    with SessionLocal() as db:

        return list(
            db.scalars(
                select(User).order_by(User.id.desc())
            ).all()
        )