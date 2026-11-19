import html
import math

import streamlit as st

from api.transactions import predict_transaction


# =========================================================
# DESIGN TOKENS — đồng bộ với app.py (Modern Blue)
# =========================================================
INK = "#172B4D"
MUTED = "#526581"
LINE = "#E1E8F3"
ACCENT = "#2563EB"
ACCENT_SOFT = "#EAF2FF"
FRAUD = "#F43F5E"
FRAUD_DEEP = "#BE123C"
FRAUD_SOFT = "#FFF1F3"
SAFE = "#10B981"
SAFE_DEEP = "#047857"
SAFE_SOFT = "#E7FAF3"

AGE_LABELS = {
    "0": "Nhóm 0 (≤ 18 tuổi)",
    "1": "Nhóm 1 (19–25 tuổi)",
    "2": "Nhóm 2 (26–35 tuổi)",
    "3": "Nhóm 3 (36–45 tuổi)",
    "4": "Nhóm 4 (46–55 tuổi)",
    "5": "Nhóm 5 (56–65 tuổi)",
    "6": "Nhóm 6 (Trên 65 tuổi)",
    "U": "Nhóm U (Không xác định)",
}

GENDER_LABELS = {
    "M": "M (Nam)",
    "F": "F (Nữ)",
    "U": "U (Không xác định)",
    "E": "E (Doanh nghiệp)",
}

CATEGORIES = [
    "es_barsandrestaurants",
    "es_contents",
    "es_fashion",
    "es_food",
    "es_health",
    "es_home",
    "es_hotelservices",
    "es_hyper",
    "es_leisure",
    "es_otherservices",
    "es_sportsandtoys",
    "es_tech",
    "es_transportation",
    "es_travel",
    "es_wellnessandbeauty",
]


CATEGORY_LABELS = {
    "es_barsandrestaurants": "es_barsandrestaurants (Quán bar và nhà hàng)",
    "es_contents": "es_contents (Nội dung và sản phẩm số)",
    "es_fashion": "es_fashion (Thời trang)",
    "es_food": "es_food (Thực phẩm)",
    "es_health": "es_health (Y tế, sức khỏe)",
    "es_home": "es_home (Đồ dùng gia đình)",
    "es_hotelservices": "es_hotelservices (Dịch vụ khách sạn)",
    "es_hyper": "es_hyper (Siêu thị)",
    "es_leisure": "es_leisure (Giải trí)",
    "es_otherservices": "es_otherservices (Các dịch vụ khác)",
    "es_sportsandtoys": "es_sportsandtoys (Thể thao và đồ chơi)",
    "es_tech": "es_tech (Công nghệ)",
    "es_transportation": "es_transportation (Vận tải, di chuyển)",
    "es_travel": "es_travel (Du lịch)",
    "es_wellnessandbeauty": "es_wellnessandbeauty (Chăm sóc sức khỏe và sắc đẹp)",
}


def _esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def _inject_css():
    st.markdown(
        f"""
        <style>
        /* ---------- Times New Roman: Predict page ---------- */
        .pd-section, .pd-caption, .pd-step, .pd-step-num,
        .pd-result, .pd-result-label, .pd-result-value, .pd-result-desc,
        .pd-kpis, .pd-kpi-label, .pd-kpi-value, .pd-kpi-sub,
        .pd-gauge, .pd-gauge-head, .pd-gauge-head b,
        .pd-track, .pd-marker, .pd-marker::after, .pd-legend,
        .pd-details, .pd-detail, .pd-detail-label, .pd-detail-value,
        .pd-detail-value code, .pd-footer {{
            font-family: "Times New Roman", Times, serif !important;
        }}

        /* Streamlit form: chỉ áp dụng cho nội dung chữ, không ghi đè icon */
        [data-testid="stForm"] label p,
        [data-testid="stForm"] input,
        [data-testid="stForm"] input::placeholder,
        [data-testid="stForm"] [data-baseweb="select"] [role="combobox"],
        [data-testid="stForm"] [data-baseweb="select"] [role="option"],
        [data-testid="stForm"] button:not([data-testid="stNumberInputStepUp"]):not([data-testid="stNumberInputStepDown"]),
        [data-testid="stAlert"] p {{
            font-family: "Times New Roman", Times, serif !important;
        }}

        /* ---------- 6 ô nhập nền trắng ---------- */
        [data-testid="stForm"] div[data-baseweb="select"] > div,
        [data-testid="stForm"] div[data-baseweb="input"],
        [data-testid="stForm"] div[data-baseweb="input"] > div,
        [data-testid="stForm"] input,
        [data-testid="stForm"] [data-testid="stNumberInput"] button {{
            background: #FFFFFF !important;
        }}

        [data-testid="stForm"] [data-testid="stNumberInput"] button:hover {{
            background: {ACCENT_SOFT} !important;
            color: {ACCENT} !important;
        }}

        .pd-section {{
            font-family: "Times New Roman", Times, serif !important;
            color: {INK};
            font-size: 1.28rem;
            font-weight: 700;
            letter-spacing: -.01em;
            margin: .4rem 0 .15rem 0;
        }}

        .pd-caption {{
            color: {MUTED};
            font-size: .88rem;
            margin-bottom: 1rem;
        }}

        .pd-step {{
            display: flex;
            align-items: center;
            gap: 10px;
            color: {ACCENT};
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .14em;
            text-transform: uppercase;
            margin: 2px 0 12px 0;
        }}

        .pd-step-num {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 24px;
            height: 24px;
            border-radius: 7px;
            background: {ACCENT_SOFT};
            color: {ACCENT};
            font-size: .72rem;
            letter-spacing: 0;
        }}

        /* ---------- Result banner ---------- */
        .pd-result {{
            display: flex;
            align-items: center;
            gap: 20px;
            padding: 24px 26px;
            border-radius: 16px;
            border: 1px solid;
            margin: 6px 0 18px 0;
        }}

        .pd-result.fraud {{ background: {FRAUD_SOFT}; border-color: #FECDD3; }}
        .pd-result.safe  {{ background: {SAFE_SOFT};  border-color: #A7F3D0; }}

        .pd-result-icon {{
            flex: 0 0 56px;
            width: 56px;
            height: 56px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #FFFFFF;
            font-size: 1.6rem;
            font-weight: 800;
        }}

        .pd-result.fraud .pd-result-icon {{
            background: {FRAUD};
            box-shadow: 0 8px 20px rgba(244,63,94,.28);
        }}

        .pd-result.safe .pd-result-icon {{
            background: {SAFE};
            box-shadow: 0 8px 20px rgba(16,185,129,.28);
        }}

        .pd-result-label {{
            font-size: .7rem;
            font-weight: 700;
            letter-spacing: .16em;
            text-transform: uppercase;
        }}

        .pd-result-value {{
            font-family: "Times New Roman", Times, serif !important;
            font-size: 1.75rem;
            font-weight: 800;
            letter-spacing: -.02em;
            line-height: 1.2;
            margin: 2px 0 4px 0;
        }}

        .pd-result-desc {{
            font-size: .88rem;
            line-height: 1.6;
            opacity: .9;
        }}

        .pd-result.fraud .pd-result-label,
        .pd-result.fraud .pd-result-value,
        .pd-result.fraud .pd-result-desc {{ color: {FRAUD_DEEP}; }}

        .pd-result.safe .pd-result-label,
        .pd-result.safe .pd-result-value,
        .pd-result.safe .pd-result-desc {{ color: {SAFE_DEEP}; }}

        /* ---------- KPI cards ---------- */
        .pd-kpis {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-bottom: 22px;
        }}

        .pd-kpi {{
            background: #FFFFFF;
            border: 1px solid {LINE};
            border-top: 3px solid {ACCENT};
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 1px 2px rgba(23,43,77,.03), 0 6px 20px rgba(23,43,77,.045);
        }}

        .pd-kpi.fraud {{ border-top-color: {FRAUD}; }}
        .pd-kpi.safe  {{ border-top-color: {SAFE}; }}

        .pd-kpi-label {{
            color: {MUTED};
            font-size: .7rem;
            font-weight: 700;
            letter-spacing: .12em;
            text-transform: uppercase;
        }}

        .pd-kpi-value {{
            font-family: "Times New Roman", Times, serif !important;
            color: {INK};
            font-size: 1.9rem;
            font-weight: 800;
            letter-spacing: -.02em;
            margin-top: 6px;
            font-variant-numeric: tabular-nums;
        }}

        .pd-kpi-sub {{
            color: {MUTED};
            font-size: .76rem;
            margin-top: 2px;
        }}

        /* ---------- Risk gauge ---------- */
        .pd-gauge {{
            background: #FFFFFF;
            border: 1px solid {LINE};
            border-radius: 14px;
            padding: 20px 22px 16px 22px;
            box-shadow: 0 1px 2px rgba(23,43,77,.03), 0 6px 20px rgba(23,43,77,.045);
        }}

        .pd-gauge-head {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            font-size: .85rem;
            color: {MUTED};
            font-weight: 600;
        }}

        .pd-gauge-head b {{
            color: {INK};
            font-size: 1.05rem;
        }}

        .pd-track {{
            position: relative;
            height: 12px;
            background: #EDF2FA;
            border-radius: 999px;
            margin: 22px 0 10px 0;
        }}

        .pd-fill {{
            height: 12px;
            border-radius: 999px;
        }}

        .pd-marker {{
            position: absolute;
            top: -8px;
            height: 28px;
            width: 3px;
            background: {INK};
            transform: translateX(-50%);
            border-radius: 3px;
        }}

        .pd-marker::after {{
            content: "Ngưỡng";
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            font-size: .64rem;
            font-weight: 700;
            color: {INK};
            white-space: nowrap;
        }}

        .pd-legend {{
            display: flex;
            justify-content: space-between;
            font-size: .72rem;
            color: {MUTED};
        }}

        /* ---------- Detail cards ---------- */
        .pd-details {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
        }}

        .pd-detail {{
            background: #FFFFFF;
            border: 1px solid {LINE};
            border-radius: 12px;
            padding: 14px 16px;
        }}

        .pd-detail-label {{
            color: {MUTED};
            font-size: .68rem;
            font-weight: 700;
            letter-spacing: .1em;
            text-transform: uppercase;
        }}

        .pd-detail-value {{
            color: {INK};
            font-size: .98rem;
            font-weight: 700;
            margin-top: 5px;
            word-break: break-word;
        }}

        .pd-detail-value code {{
            background: {ACCENT_SOFT};
            color: {ACCENT};
            padding: 2px 8px;
            border-radius: 6px;
            font-size: .85rem;
        }}

        .pd-footer {{
            text-align: center;
            color: #94A3B8;
            font-size: .74rem;
            letter-spacing: .06em;
            padding: 10px;
        }}

        @media (max-width: 900px) {{
            .pd-kpis {{ grid-template-columns: 1fr; }}
            .pd-details {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        }}



/* ===== PREDICT FORM: TYPOGRAPHY 20PX ===== */

/* Tiêu đề chính */
.pd-section {{
    font-family: "Times New Roman", Times, serif !important;
    font-size: 30px !important;
    font-weight: 700 !important;
}}

/* Mô tả */
.pd-caption {{
    font-family: "Times New Roman", Times, serif !important;
    font-size: 20px !important;
    line-height: 1.5 !important;
}}

/* Tiêu đề nhóm 01 và 02 */
.pd-step,
.pd-step .pd-step-text,
.pd-step .pd-step-num {{
    font-family: "Times New Roman", Times, serif !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    letter-spacing: 0 !important;
    line-height: 1.4 !important;
}}

/* Nhãn của 6 trường nhập */
[data-testid="stForm"] label p {{
    font-family: "Times New Roman", Times, serif !important;
    font-size: 20px !important;
    font-weight: 600 !important;
}}


/* Nội dung bên trong các ô nhập: 16px */
[data-testid="stForm"] input,
[data-testid="stForm"] input::placeholder {{
    font-family: "Times New Roman", Times, serif !important;
    font-size: 16px !important;
    font-weight: 400 !important;
}}

/* Nội dung bên trong các ô lựa chọn: 16px */
[data-testid="stForm"]
[data-baseweb="select"] [role="combobox"],
[data-testid="stForm"]
[data-baseweb="select"] [role="combobox"] * {{
    font-family: "Times New Roman", Times, serif !important;
    font-size: 16px !important;
    font-weight: 400 !important;
}}


/* Nút phân tích */
[data-testid="stFormSubmitButton"] button,
[data-testid="stFormSubmitButton"] button p {{
    font-family: "Times New Roman", Times, serif !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    line-height: 1.4 !important;
}}

/* Không làm thay đổi kích thước icon */
[data-testid="stForm"] svg {{
    flex-shrink: 0;
}}



        </style>
        """,
        unsafe_allow_html=True,
    )



def _step_title(num: str, text: str):
    st.markdown(
        f"""
        <div class="pd-step">
            <span class="pd-step-num">{html.escape(num)}</span>
            <span class="pd-step-text">{html.escape(text)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _section(title: str, caption: str = ""):
    st.markdown(f'<div class="pd-section">{title}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="pd-caption">{caption}</div>', unsafe_allow_html=True)


# =========================================================
# PAGE
# =========================================================
def predict_page():

    # -------------------------------------
    # SESSION STATE
    # -------------------------------------
    if "prediction_result" not in st.session_state:
        st.session_state.prediction_result = None

    if "prediction_transaction" not in st.session_state:
        st.session_state.prediction_transaction = None

    if "prediction_error" not in st.session_state:
        st.session_state.prediction_error = None

    _inject_css()

    # Tiêu đề trang đã được app.py hiển thị qua page_header(),
    # nên ở đây không lặp lại st.title nữa.

    # =========================================================
    # 1. TRANSACTION INPUT FORM
    # =========================================================
    _section(
        "Thông tin giao dịch",
        "Cung cấp đầy đủ thông tin để hệ thống thực hiện phân tích.",
    )

    with st.container(border=True):

        with st.form("prediction_form", clear_on_submit=False):

            _step_title("01", "Khách hàng và thời điểm")

            col1, col2, col3 = st.columns(3, gap="large")

            with col1:
                step = st.number_input(
                    "Step (thời điểm giao dịch)",
                    min_value=0,
                    value=105,
                    step=1,
                    help="Thời điểm giao dịch theo dữ liệu đầu vào của hệ thống.",
                    key="predict_step",
                )

            with col2:
                age = st.selectbox(
                    "Nhóm tuổi",
                    options=list(AGE_LABELS.keys()),
                    format_func=lambda x: AGE_LABELS[x],
                    help="Chọn nhóm tuổi tương ứng theo bộ dữ liệu BankSim.",
                    key="predict_age",
                )

            with col3:
                gender = st.selectbox(
                    "Giới tính",
                    options=list(GENDER_LABELS.keys()),
                    format_func=lambda x: GENDER_LABELS[x],
                    help="Chọn mã giới tính theo bộ dữ liệu.",
                    key="predict_gender",
                )

            st.divider()

            _step_title("02", "Chi tiết giao dịch")

            col1, col2, col3 = st.columns(3, gap="large")

            with col1:
                merchant = st.text_input(
                    "Mã Merchant",
                    value="M123456",
                    placeholder="Ví dụ: M123456",
                    help="Mã định danh đơn vị chấp nhận giao dịch.",
                    key="predict_merchant",
                )

            with col2:
                amount = st.number_input(
                    "Số tiền giao dịch",
                    min_value=0.0,
                    value=200.0,
                    step=10.0,
                    format="%.2f",
                    help="Giá trị giao dịch cần phân tích.",
                    key="predict_amount",
                )

            with col3:
                category = st.selectbox(
                    "Danh mục giao dịch",
                    options=CATEGORIES,
                    index=12,
                    format_func=lambda x: CATEGORY_LABELS.get(x, x),
                    help="Chọn danh mục tương ứng với giao dịch.",
                    key="predict_category",
                )

            st.write("")

            submitted = st.form_submit_button(
                "Phân tích giao dịch",
                use_container_width=True,
                type="primary",
            )

    # =========================================================
    # 2. PREDICTION PROCESSING  (giữ nguyên logic)
    # =========================================================
    if submitted:

        st.session_state.prediction_result = None
        st.session_state.prediction_transaction = None
        st.session_state.prediction_error = None

        if not merchant.strip():
            st.session_state.prediction_error = "Vui lòng nhập mã Merchant."

        elif not category.strip():
            st.session_state.prediction_error = "Vui lòng chọn danh mục giao dịch."

        elif not math.isfinite(float(amount)):
            st.session_state.prediction_error = "Số tiền giao dịch không hợp lệ."

        else:
            transaction_data = {
                "step": int(step),
                "age": age,
                "gender": gender,
                "merchant": merchant.strip(),
                "category": category.strip(),
                "amount": float(amount),
            }

            token = st.session_state.access_token

            if not token:
                st.session_state.prediction_error = (
                    "Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại."
                )

            else:
                try:
                    with st.spinner("XGBoost đang phân tích giao dịch..."):
                        result = predict_transaction(token, transaction_data)

                    if not isinstance(result, dict):
                        st.session_state.prediction_error = (
                            "Phản hồi từ Backend không hợp lệ."
                        )

                    elif "error" in result:
                        st.session_state.prediction_error = str(result["error"])

                    else:
                        required_fields = [
                            "fraud_probability",
                            "predicted_label",
                            "threshold",
                        ]

                        if not all(field in result for field in required_fields):
                            st.session_state.prediction_error = (
                                "Backend thiếu dữ liệu kết quả dự đoán."
                            )

                        else:
                            try:
                                fraud_probability = float(result["fraud_probability"])
                                predicted_label = int(result["predicted_label"])
                                threshold = float(result["threshold"])

                                if not all([
                                    math.isfinite(fraud_probability),
                                    math.isfinite(threshold),
                                ]):
                                    raise ValueError("Giá trị xác suất không hợp lệ.")

                                if not (
                                    0 <= fraud_probability <= 1
                                    and 0 <= threshold <= 1
                                ):
                                    raise ValueError(
                                        "Xác suất hoặc threshold nằm ngoài khoảng hợp lệ."
                                    )

                                if predicted_label not in (0, 1):
                                    raise ValueError("Nhãn dự đoán không hợp lệ.")

                                st.session_state.prediction_result = {
                                    "fraud_probability": fraud_probability,
                                    "predicted_label": predicted_label,
                                    "threshold": threshold,
                                }
                                st.session_state.prediction_transaction = (
                                    transaction_data.copy()
                                )

                            except (ValueError, TypeError, OverflowError) as e:
                                st.session_state.prediction_error = (
                                    f"Dữ liệu dự đoán không hợp lệ: {e}"
                                )

                except Exception as e:
                    st.session_state.prediction_error = (
                        f"Không thể kết nối hoặc xử lý yêu cầu: {e}"
                    )

    # =========================================================
    # 3. ERROR
    # =========================================================
    if st.session_state.prediction_error:
        st.error(st.session_state.prediction_error, icon="⚠️")

    # =========================================================
    # 4. RESULT
    # =========================================================
    prediction = st.session_state.prediction_result
    transaction = st.session_state.prediction_transaction

    if prediction and transaction:

        probability = prediction["fraud_probability"]
        label = prediction["predicted_label"]
        threshold = prediction["threshold"]

        probability_percent = probability * 100
        threshold_percent = threshold * 100
        is_fraud = label == 1
        tone = "fraud" if is_fraud else "safe"

        st.write("")
        _section("Kết quả phân tích", "Kết luận của mô hình XGBoost cho giao dịch vừa nhập.")

        # -------- Result banner --------
        if is_fraud:
            icon, tag, verdict, desc = (
                "!",
                "Fraud detected",
                "Gian lận",
                "Mô hình phân loại giao dịch này có dấu hiệu gian lận. "
                "Cần kiểm tra thêm trước khi đưa ra quyết định xử lý.",
            )
        else:
            icon, tag, verdict, desc = (
                "✓",
                "Transaction normal",
                "Bình thường",
                "Mô hình phân loại giao dịch này vào nhóm bình thường "
                "theo ngưỡng phân loại hiện tại.",
            )

        st.markdown(
            f"""
            <div class="pd-result {tone}">
                <div class="pd-result-icon">{icon}</div>
                <div>
                    <div class="pd-result-label">{tag}</div>
                    <div class="pd-result-value">{verdict}</div>
                    <div class="pd-result-desc">{desc}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -------- KPI cards --------
        gap = probability_percent - threshold_percent
        gap_text = f"{'Cao hơn' if gap >= 0 else 'Thấp hơn'} ngưỡng {abs(gap):.2f} điểm %"

        st.markdown(
            f"""
            <div class="pd-kpis">
                <div class="pd-kpi {tone}">
                    <div class="pd-kpi-label">Xác suất gian lận</div>
                    <div class="pd-kpi-value">{probability_percent:.2f}%</div>
                    <div class="pd-kpi-sub">{gap_text}</div>
                </div>
                <div class="pd-kpi">
                    <div class="pd-kpi-label">Ngưỡng phân loại</div>
                    <div class="pd-kpi-value">{threshold_percent:.2f}%</div>
                    <div class="pd-kpi-sub">Do Backend trả về</div>
                </div>
                <div class="pd-kpi {tone}">
                    <div class="pd-kpi-label">Kết quả mô hình</div>
                    <div class="pd-kpi-value">{verdict}</div>
                    <div class="pd-kpi-sub">XGBoost classifier</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


        # -------- Explanation --------
        if is_fraud:
            st.warning(
                f"Xác suất gian lận ({probability_percent:.2f}%) lớn hơn hoặc bằng "
                f"ngưỡng phân loại ({threshold_percent:.2f}%). "
                "Vì vậy, mô hình đưa ra kết luận: GIAN LẬN."
            )
        else:
            st.success(
                f"Xác suất gian lận ({probability_percent:.2f}%) nhỏ hơn "
                f"ngưỡng phân loại ({threshold_percent:.2f}%). "
                "Vì vậy, mô hình đưa ra kết luận: BÌNH THƯỜNG."
            )

        st.info(
            "Lưu ý: Xác suất là mức độ dự đoán của mô hình, không phải bằng chứng "
            "xác nhận giao dịch thực sự gian lận. Kết quả cần được xem xét cùng "
            "các biện pháp kiểm tra khác."
        )

