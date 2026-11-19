import pandas as pd
from io import BytesIO
from pydantic import ValidationError

from app.backend.schemas import CSVTransactionRow


REQUIRED_COLUMNS = [
    "step",
    "age",
    "gender",
    "merchant",
    "category",
    "amount"
]


def read_and_validate_csv(file_content: bytes):
    # Đọc file CSV
    try:
        df = pd.read_csv(BytesIO(file_content))
    except Exception:
        raise ValueError("Cannot read CSV file")

    # Kiểm tra các cột bắt buộc
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {', '.join(missing_columns)}"
        )

    if df.empty:
        raise ValueError("CSV file is empty")

    # Chỉ lấy 6 cột cần thiết
    # Chỉ lấy 6 cột cần thiết
    df = df[REQUIRED_COLUMNS].copy()

# Chuẩn hóa các cột dạng chuỗi
    string_columns = [
        "age",
        "gender",
        "merchant",
        "category"
]

    for column in string_columns:
        df[column] = df[column].astype("string")

    # Kiểm tra từng dòng
    validated_rows = []

    for index, row in df.iterrows():
        row_data = row.to_dict()

        try:
            validated_row = CSVTransactionRow(**row_data)
            validated_rows.append(
                validated_row.model_dump()
            )
        except ValidationError as error:
            raise ValueError(
                f"Invalid data at row {index + 2}: {error}"
            )

    return validated_rows