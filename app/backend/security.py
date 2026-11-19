
from pwdlib import PasswordHash

# Khởi tạo thuật toán băm mật khẩu mặc định an toàn
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Băm mật khẩu trước khi lưu vào database."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Kiểm tra mật khẩu nhập vào có khớp với mật khẩu đã băm không."""
    return password_hash.verify(plain_password, hashed_password)
