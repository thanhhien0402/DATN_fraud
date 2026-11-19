
from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException
)

from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.backend.database import get_db

from app.backend.models import (
    Transaction,
    Prediction,
    AnalysisBatch,
    User
)

from app.backend.schemas import (
    TransactionCreate,
    TransactionPredictionResponse,
    TransactionHistoryResponse,
    TransactionStatisticsResponse
)

from app.backend.dependencies import get_current_user
from app.backend.model_loader import load_xgboost_artifacts
from app.backend.prediction_service import predict_transaction


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


# Load model once when the API starts
model, encoder, model_features, threshold = load_xgboost_artifacts()


# =========================================================
# 1. CREATE MANUAL TRANSACTION
# POST /transactions
# =========================================================

@router.post(
    "",
    response_model=TransactionPredictionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction_dict = transaction_data.model_dump()
    transaction_dict["amount"] = float(transaction_dict["amount"])

    try:
        new_transaction = Transaction(
            user_id=current_user.id,
            step=transaction_data.step,
            age=transaction_data.age,
            gender=transaction_data.gender,
            merchant=transaction_data.merchant,
            category=transaction_data.category,
            amount=transaction_data.amount,
            source="manual",
            actual_fraud=None
        )

        db.add(new_transaction)
        db.flush()

        prediction_result = predict_transaction(
            transaction=transaction_dict,
            model=model,
            encoder=encoder,
            model_features=model_features,
            threshold=threshold
        )

        new_prediction = Prediction(
            transaction_id=new_transaction.id,
            model_name="XGBoost",
            fraud_probability=prediction_result["fraud_probability"],
            predicted_label=prediction_result["predicted_label"],
            threshold=prediction_result["threshold"]
        )

        db.add(new_prediction)

        db.commit()
        db.refresh(new_transaction)

        return {
            "transaction": new_transaction,
            "fraud_probability": prediction_result["fraud_probability"],
            "predicted_label": prediction_result["predicted_label"],
            "threshold": prediction_result["threshold"]
        }

    except Exception:
        db.rollback()
        raise


# =========================================================
# 2. GET TRANSACTION HISTORY
# GET /transactions
# =========================================================

@router.get(
    "",
    response_model=list[TransactionHistoryResponse]
)
def get_transaction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = (
        db.query(Transaction, Prediction)
        .join(
            Prediction,
            Prediction.transaction_id == Transaction.id
        )
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    history = []

    for transaction, prediction in results:
        history.append({
            "transaction": transaction,
            "fraud_probability": prediction.fraud_probability,
            "predicted_label": prediction.predicted_label,
            "threshold": prediction.threshold,
            "model_name": prediction.model_name
        })

    return history


# =========================================================
# 3. GET TRANSACTION STATISTICS
# GET /transactions/statistics
# =========================================================

@router.get(
    "/statistics",
    response_model=TransactionStatisticsResponse
)
def get_transaction_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = (
        db.query(
            func.count(Prediction.id),
            func.sum(
                case(
                    (Prediction.predicted_label == 1, 1),
                    else_=0
                )
            )
        )
        .join(
            Transaction,
            Transaction.id == Prediction.transaction_id
        )
        .filter(Transaction.user_id == current_user.id)
        .first()
    )

    total_transactions = result[0] or 0
    fraud_transactions = int(result[1] or 0)

    normal_transactions = (
        total_transactions - fraud_transactions
    )

    fraud_rate = (
        fraud_transactions / total_transactions * 100
        if total_transactions > 0
        else 0.0
    )

    total_batches = (
        db.query(func.count(AnalysisBatch.id))
        .filter(AnalysisBatch.user_id == current_user.id)
        .scalar()
    )

    return {
        "total_transactions": total_transactions,
        "fraud_transactions": fraud_transactions,
        "normal_transactions": normal_transactions,
        "fraud_rate": round(fraud_rate, 2),
        "total_batches": total_batches or 0
    }


# =========================================================
# 4. GET TRANSACTION DETAIL
# GET /transactions/{transaction_id}
# Keep this dynamic route LAST
# =========================================================

@router.get(
    "/{transaction_id}",
    response_model=TransactionHistoryResponse
)
def get_transaction_detail(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = (
        db.query(Transaction, Prediction)
        .join(
            Prediction,
            Prediction.transaction_id == Transaction.id
        )
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
        .first()
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    transaction, prediction = result

    return {
        "transaction": transaction,
        "fraud_probability": prediction.fraud_probability,
        "predicted_label": prediction.predicted_label,
        "threshold": prediction.threshold,
        "model_name": prediction.model_name
    }
