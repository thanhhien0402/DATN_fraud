
import requests

API_BASE_URL = "https://banksim-fraud-backend.onrender.com"


def get_auth_headers(token: str):
    """Tạo header xác thực bằng JWT."""
    return {
        "Authorization": f"Bearer {token}"
    }


def get_statistics(token: str):
    """Lấy thống kê giao dịch của người dùng hiện tại."""

    url = f"{API_BASE_URL}/transactions/statistics"

    try:
        response = requests.get(
            url,
            headers=get_auth_headers(token),
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 401:
            return {"error": "Phiên đăng nhập đã hết hạn."}

        return {
            "error": f"Lỗi lấy thống kê: HTTP {response.status_code}"
        }

    except requests.exceptions.ConnectionError:
        return {"error": "Không thể kết nối đến Backend FastAPI."}

    except requests.exceptions.Timeout:
        return {"error": "Máy chủ phản hồi quá thời gian chờ."}

    except requests.exceptions.RequestException as error:
        return {"error": f"Lỗi kết nối: {error}"}


def get_transaction_history(token: str):
    """Lấy lịch sử giao dịch của người dùng hiện tại."""

    url = f"{API_BASE_URL}/transactions"

    try:
        response = requests.get(
            url,
            headers=get_auth_headers(token),
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 401:
            return {"error": "Phiên đăng nhập đã hết hạn."}

        return {
            "error": f"Lỗi lấy lịch sử: HTTP {response.status_code}"
        }

    except requests.exceptions.ConnectionError:
        return {"error": "Không thể kết nối đến Backend FastAPI."}

    except requests.exceptions.Timeout:
        return {"error": "Máy chủ phản hồi quá thời gian chờ."}

    except requests.exceptions.RequestException as error:
        return {"error": f"Lỗi kết nối: {error}"}

def predict_transaction(token: str, transaction_data: dict):
    """
    Gửi thông tin giao dịch đến FastAPI
    để lưu giao dịch và dự đoán gian lận bằng XGBoost.
    """

    url = f"{API_BASE_URL}/transactions"

    try:
        response = requests.post(
            url,
            json=transaction_data,
            headers=get_auth_headers(token),
            timeout=15
        )

        if response.status_code in (200, 201):
            return response.json()

        if response.status_code == 401:
            return {"error": "Phiên đăng nhập đã hết hạn."}

        try:
            error_detail = response.json().get(
                "detail",
                response.text
            )
        except ValueError:
            error_detail = response.text

        return {
            "error": f"Lỗi dự đoán: HTTP {response.status_code} - {error_detail}"
        }

    except requests.exceptions.ConnectionError:
        return {"error": "Không thể kết nối đến Backend FastAPI."}

    except requests.exceptions.Timeout:
        return {"error": "Máy chủ phản hồi quá thời gian chờ."}

    except requests.exceptions.RequestException as error:
        return {"error": f"Lỗi kết nối: {error}"}

