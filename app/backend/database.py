
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

# Đọc thông tin từ file .env ở thư mục gốc dự án
load_dotenv()

# Lấy thông tin kết nối PostgreSQL
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Kiểm tra cấu hình
required_settings = {
    "DB_HOST": DB_HOST,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
}

missing_settings = [
    key for key, value in required_settings.items() if not value
]

if missing_settings:
    raise ValueError(
        f"Missing database settings: {', '.join(missing_settings)}"
    )

# Tạo URL kết nối an toàn
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

# Khởi tạo engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Quản lý phiên làm việc với database
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base dùng để khai báo các bảng bằng SQLAlchemy
Base = declarative_base()


# Hàm kiểm tra kết nối PostgreSQL
def test_connection():
    from sqlalchemy import text

    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        )
        database_name, username = result.fetchone()

        print("PostgreSQL connection successful!")
        print(f"Database: {database_name}")
        print(f"Username: {username}")


# Dependency cung cấp database session cho API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
