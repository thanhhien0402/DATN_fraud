
from fastapi import FastAPI
from app.backend.routes.transactions import router as transactions_router
from app.backend.routes.auth import router as auth_router


# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="BankSim Fraud Detection API",
    description="API for detecting fraudulent bank transactions",
    version="1.0.0"
)

# Kết nối router xác thực tài khoản
app.include_router(auth_router)
app.include_router(transactions_router)

# API kiểm tra trạng thái hệ thống
@app.get("/")
def home():
    return {
        "message": "BankSim Fraud Detection API is running!"
    }


# API kiểm tra sức khỏe hệ thống
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
