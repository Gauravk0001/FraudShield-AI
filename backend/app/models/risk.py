import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum

class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    fraud_probability: Mapped[float] = mapped_column(Float, nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False) # 0 to 100
    risk_level: Mapped[RiskLevel] = mapped_column(SQLEnum(RiskLevel), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), default="v1.0.0", nullable=False)
    behavioral_flags: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="risk_score")
    explanation: Mapped["RiskExplanation"] = relationship("RiskExplanation", back_populates="risk_score_obj", uselist=False)

class RiskExplanation(Base):
    __tablename__ = "risk_explanations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    risk_score_id: Mapped[str] = mapped_column(String(36), ForeignKey("risk_scores.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    shap_values: Mapped[dict] = mapped_column(JSON, nullable=False) # structured feature contributions
    top_factors: Mapped[dict] = mapped_column(JSON, nullable=False) # human readable top factors
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    risk_score_obj: Mapped["RiskScore"] = relationship("RiskScore", back_populates="explanation")
