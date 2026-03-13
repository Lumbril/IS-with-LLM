from typing import Optional

from sqlalchemy import Float, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Log
from models.base import BaseModel


class Anomaly(BaseModel):
    __tablename__ = "anomalies"

    log_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("logs.id"), index=True, nullable=True
    )

    severity: Mapped[str] = mapped_column(
        String(20)
    )

    description: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )

    log: Mapped[Optional[Log]] = relationship(
        back_populates="anomalies"
    )
