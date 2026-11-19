
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from decimal import Decimal
from datetime import datetime

# ==========================================
# USER REGISTRATION
# ==========================================
class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


# ==========================================
# USER LOGIN
# ==========================================
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ==========================================
# USER RESPONSE
# ==========================================
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# TRANSACTION INPUT
# ==========================================
class TransactionCreate(BaseModel):
    step: int = Field(ge=0)

    age: str = Field(min_length=1, max_length=10)

    gender: str = Field(min_length=1, max_length=10)

    merchant: str = Field(min_length=1, max_length=100)

    category: str = Field(min_length=1, max_length=100)

    amount: Decimal = Field(
        ge=0,
        max_digits=15,
        decimal_places=2
    )
class TransactionResponse(BaseModel):
    id: int
    user_id: int
    batch_id: int | None
    step: int
    age: str
    gender: str
    merchant: str
    category: str
    amount: Decimal
    source: str
    actual_fraud: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
class TransactionPredictionResponse(BaseModel):
    transaction: TransactionResponse
    fraud_probability: Decimal
    predicted_label: int
    threshold: Decimal
class TransactionHistoryResponse(BaseModel):
    transaction: TransactionResponse
    fraud_probability: Decimal
    predicted_label: int
    threshold: Decimal
    model_name: str
class CSVTransactionRow(BaseModel):
    step: int = Field(ge=0)
    age: str = Field(min_length=1, max_length=10)
    gender: str = Field(min_length=1, max_length=10)
    merchant: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(
        ge=0,
        max_digits=15,
        decimal_places=2
    )
class TransactionStatisticsResponse(BaseModel):
    total_transactions: int
    fraud_transactions: int
    normal_transactions: int
    fraud_rate: float
    total_batches: int