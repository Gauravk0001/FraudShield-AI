import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum

class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    FLAGGED = "FLAGGED"

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    transaction_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    merchant_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[TransactionStatus] = mapped_column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    features: Mapped["TransactionFeature"] = relationship("TransactionFeature", back_populates="transaction", uselist=False)
    risk_score: Mapped["RiskScore"] = relationship("RiskScore", back_populates="transaction", uselist=False)
    alert: Mapped["Alert"] = relationship("Alert", back_populates="transaction", uselist=False)

class TransactionFeature(Base):
    __tablename__ = "transaction_features"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    features_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="features")
