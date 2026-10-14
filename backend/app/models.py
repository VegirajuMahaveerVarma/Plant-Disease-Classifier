from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Scan(Base):
    __tablename__ = "scans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), default="plant-image")
    predicted_class: Mapped[str] = mapped_column(String(255))
    confidence: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(40), default="prediction")
    model_version: Mapped[str] = mapped_column(String(80), default="unknown")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
