from typing import Optional

from sqlalchemy import Float, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class Anomaly(BaseModel):
    __tablename__ = "anomalies"

    log_id: Mapped[int] = mapped_column(
        ForeignKey("logs.id"),
        index=True
    )

    anomaly_type: Mapped[str] = mapped_column(
        String(50)
    )

    risk_score: Mapped[float] = mapped_column(
        Float
    )

    mitre_technique: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    explanation: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True
    )

    log: Mapped["Log"] = relationship(
        back_populates="anomalies"
    )
