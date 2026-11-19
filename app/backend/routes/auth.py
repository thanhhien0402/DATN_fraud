
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.backend.database import get_db
from app.backend.models import User
from app.backend.schemas import UserRegister, UserResponse
from app.backend.security import hash_password

from fastapi.security import OAuth2PasswordRequestForm
from app.backend.dependencies import get_current_user
from app.backend.security import verify_password
from app.backend.auth_utils import create_access_token
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    # Kiểm tra email đã tồn tại
    existing_email = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Kiểm tra username đã tồn tại
    existing_username = (
        db.query(User)
        .filter(User.username == user_data.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Băm mật khẩu
    hashed_password = hash_password(user_data.password)

    # Tạo tài khoản mới
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Tìm tài khoản theo username
    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    # Kiểm tra tài khoản và mật khẩu
    if not user or not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Tạo JWT Access Token
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_my_account(
    current_user: User = Depends(get_current_user)
):
    """
    Trả về thông tin tài khoản đang đăng nhập.
    """
    return current_user
