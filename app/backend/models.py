
from sqlalchemy import (
    BigInteger,
    Integer,
    SmallInteger,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    CheckConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.backend.database import Base


# ==========================================
# 1. USERS
# ==========================================
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    transactions = relationship(
        "Transaction", back_populates="user",
        cascade="all, delete-orphan"
    )
    analysis_batches = relationship(
        "AnalysisBatch", back_populates="user",
        cascade="all, delete-orphan"
    )


# ==========================================
# 2. ANALYSIS BATCHES
# ==========================================
class AnalysisBatch(Base):
    __tablename__ = "analysis_batches"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    file_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    total_records: Mapped[int] = mapped_column(
        Integer, server_default=text("0")
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="analysis_batches")
    transactions = relationship(
        "Transaction", back_populates="batch"
    )


# ==========================================
# 3. TRANSACTIONS
# ==========================================
class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    batch_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("analysis_batches.id", ondelete="SET NULL"),
        nullable=True
    )

    step: Mapped[int] = mapped_column(Integer, nullable=False)
    age: Mapped[str] = mapped_column(String(10), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    merchant: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    source: Mapped[str] = mapped_column(
        String(20), server_default=text("'manual'"), nullable=False
    )
    actual_fraud: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="transactions")
    batch = relationship("AnalysisBatch", back_populates="transactions")
    predictions = relationship(
        "Prediction",
        back_populates="transaction",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("step >= 0", name="chk_transaction_step"),
        CheckConstraint("amount >= 0", name="chk_transaction_amount"),
        CheckConstraint(
            "source IN ('manual', 'csv')",
            name="chk_transaction_source"
        ),
        CheckConstraint(
            "actual_fraud IN (0, 1) OR actual_fraud IS NULL",
            name="chk_actual_fraud"
        ),
    )


# ==========================================
# 4. PREDICTIONS
# ==========================================
class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    transaction_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False
    )
    model_name: Mapped[str] = mapped_column(
        String(50), server_default=text("'XGBoost'"), nullable=False
    )
    fraud_probability: Mapped[float] = mapped_column(
        Numeric(8, 7), nullable=False
    )
    predicted_label: Mapped[int] = mapped_column(
        SmallInteger, nullable=False
    )
    threshold: Mapped[float] = mapped_column(
        Numeric(8, 7), nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    transaction = relationship(
        "Transaction", back_populates="predictions"
    )

    __table_args__ = (
        CheckConstraint(
            "fraud_probability >= 0 AND fraud_probability <= 1",
            name="chk_fraud_probability"
        ),
        CheckConstraint(
            "predicted_label IN (0, 1)",
            name="chk_predicted_label"
        ),
        CheckConstraint(
            "threshold >= 0 AND threshold <= 1",
            name="chk_prediction_threshold"
        ),
    )
