from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True
    )

    password_hash: Mapped[str] = mapped_column(String)
