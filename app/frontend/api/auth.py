
import requests

API_BASE_URL = "http://127.0.0.1:8000"


def login_user(username: str, password: str):
    url = f"{API_BASE_URL}/auth/login"

    data = {
        "username": username,
        "password": password
    }

    try:
        response = requests.post(
            url,
            data=data,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 401:
            return {
                "error": "Tên đăng nhập hoặc mật khẩu không chính xác."
            }

        return {
            "error": f"Lỗi từ máy chủ: {response.status_code}"
        }

    except requests.exceptions.ConnectionError:
        return {
            "error": "Không thể kết nối đến Backend FastAPI."
        }

    except requests.exceptions.Timeout:
        return {
            "error": "Máy chủ phản hồi quá thời gian chờ."
        }


def get_current_user(token: str):
    url = f"{API_BASE_URL}/auth/me"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.exceptions.RequestException:
        return None


def register_user(username: str, email: str, password: str):
    url = f"{API_BASE_URL}/auth/register"

    data = {
        "username": username,
        "email": email,
        "password": password
    }

    try:
        response = requests.post(
            url,
            json=data,
            timeout=10
        )

        if response.status_code in (200, 201):
            return response.json()

        try:
            error_detail = response.json().get(
                "detail",
                "Đăng ký tài khoản thất bại."
            )
        except ValueError:
            error_detail = "Đăng ký tài khoản thất bại."

        return {
            "error": error_detail
        }

    except requests.exceptions.ConnectionError:
        return {
            "error": "Không thể kết nối đến Backend FastAPI."
        }

    except requests.exceptions.Timeout:
        return {
            "error": "Máy chủ phản hồi quá thời gian chờ."
        }

    except requests.exceptions.RequestException as error:
        return {
            "error": f"Lỗi kết nối: {error}"
        }
