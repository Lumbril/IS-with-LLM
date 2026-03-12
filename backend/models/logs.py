from typing import Optional, Dict, List

from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class Log(BaseModel):
    __tablename__ = "logs"

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        index=True
    )

    ip_address: Mapped[str] = mapped_column(
        String(45)
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    host: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    details: Mapped[Optional[Dict]] = mapped_column(
        JSON,
        nullable=True
    )

    anomalies: Mapped[List["Anomaly"]] = relationship(
        back_populates="log"
    )
