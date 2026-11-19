import html

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from api.auth import login_user, get_current_user, register_user
from api.transactions import get_statistics, get_transaction_history
from views.predict import predict_page


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="BankSim | Fraud Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2. DESIGN TOKENS  (Modern Blue — Bright)
# =========================================================
# Nền trắng xanh mát + xanh dương #2563EB / #EAF2FF làm màu nhấn.
# Hồng đỏ (rose) cho gian lận, xanh ngọc (emerald) cho bình thường.
INK = "#172B4D"          # chữ chính (navy)
TEXT_SOFT = "#526581"    # chữ phụ trên biểu đồ
CANVAS = "#F5F8FE"       # nền ứng dụng
PAPER = "#FFFFFF"        # bề mặt card
SIDEBAR = "#FFFFFF"      # nền sidebar
LINE = "#E1E8F3"         # viền
LINE_SOFT = "#EDF2FA"
MUTED = "#526581"
ACCENT = "#2563EB"       # blue
ACCENT_DEEP = "#1D4ED8"
ACCENT_SOFT = "#EAF2FF"
SAND = "#D6E4FF"         # điểm nhấn phụ (sky)
SAND_SOFT = "#E6F6FF"
FRAUD = "#F43F5E"        # rose
FRAUD_SOFT = "#FFF1F3"
SAFE = "#10B981"         # emerald
SAFE_SOFT = "#E7FAF3"

FONT_SANS = "'Times New Roman', Times, serif"
FONT_DISPLAY = "'Times New Roman', Times, serif"


st.markdown(
    f"""
    <style>
    :root {{
        --ink: {INK};
        --canvas: {CANVAS};
        --paper: {PAPER};
        --line: {LINE};
        --line-soft: {LINE_SOFT};
        --muted: {MUTED};
        --accent: {ACCENT};
        --accent-deep: {ACCENT_DEEP};
        --accent-soft: {ACCENT_SOFT};
        --sand: {SAND};
        --sand-soft: {SAND_SOFT};
        --fraud: {FRAUD};
        --fraud-soft: {FRAUD_SOFT};
        --safe: {SAFE};
        --safe-soft: {SAFE_SOFT};
        --display: {FONT_DISPLAY};
        --sans: {FONT_SANS};
        --radius: 14px;
        --shadow: 0 1px 2px rgba(15,23,42,.03), 0 6px 20px rgba(15,23,42,.045);
    }}
    /* ===== GLOBAL FONT: TIMES NEW ROMAN ===== */

html, body, .stApp,
.stApp p,
.stApp label,
.stApp button,
.stApp input,
.stApp textarea,
.stApp select,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5,
.stApp h6,
[data-testid="stSidebar"],
[data-testid="stDataFrame"] {{
    font-family: "Times New Roman", Times, serif !important;
}}
    /* ---------- Base ---------- */
    html, body, [class*="css"], .stApp {{
        font-family: var(--sans);
        -webkit-font-smoothing: antialiased;
    }}

    .stApp {{
        background:
            radial-gradient(900px 420px at 100% -8%, rgba(37,99,235,.07), transparent 60%),
            radial-gradient(700px 360px at -10% 110%, rgba(37,99,235,.04), transparent 60%),
            var(--canvas);
        color: var(--ink);
    }}

    #MainMenu, footer {{ visibility: hidden; }}

    [data-testid="stHeader"] {{ background: transparent; }}

    .block-container {{
        max-width: 1440px;
        padding-top: 2.2rem;
        padding-bottom: 3.5rem;
    }}

    h1, h2, h3 {{
        font-family: var(--display) !important;
        color: var(--ink);
        font-weight: 600 !important;
        letter-spacing: -0.015em;
    }}

    p, label, .stMarkdown {{ color: var(--ink); }}

    [data-testid="stCaptionContainer"], .stCaption {{
        color: var(--muted) !important;
    }}

    hr {{ border-color: var(--line); }}

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {{
        background: {SIDEBAR};
        border-right: 1px solid var(--line);
    }}

    [data-testid="stSidebar"] * {{ color: var(--ink); }}

    [data-testid="stSidebar"] [data-testid="stRadio"] > div {{ gap: 2px; }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        width: 100%;
        padding: 11px 14px;
        margin: 0;
        border-radius: 10px;
        border: 1px solid transparent;
        border-left: 3px solid transparent;
        transition: background .18s ease, border-color .18s ease;
        cursor: pointer;
    }}

    /* Ẩn chấm tròn mặc định của radio */
    [data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {{
        display: none;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
        background: rgba(15,23,42,.035);
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
        background: var(--accent-soft);
        border-left-color: var(--accent);
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {{
        color: var(--accent-deep) !important;
        font-weight: 600;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label p {{
        font-size: .9rem;
        font-weight: 500;
        color: #475569 !important;
    }}

    [data-testid="stSidebar"] .stButton > button {{
        background: var(--paper);
        border: 1px solid var(--line);
        color: var(--ink);
        font-weight: 500;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        border-color: var(--fraud);
        color: var(--fraud);
        background: var(--fraud-soft);
    }}

    .brand-lockup {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 6px 2px 22px 2px;
        border-bottom: 1px solid var(--line);
        margin-bottom: 18px;
    }}

    .brand-mark {{
        width: 40px;
        height: 40px;
        border-radius: 11px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #3B82F6, {ACCENT_DEEP});
        color: #FFFFFF !important;
        font-family: var(--display);
        font-size: 1.25rem;
        font-weight: 600;
        box-shadow: 0 6px 16px rgba(37,99,235,.25);
    }}

    .brand-name {{
        color: var(--ink) !important;
        font-family: var(--display);
        font-size: 1.12rem;
        font-weight: 600;
        letter-spacing: -.01em;
        line-height: 1.15;
    }}

    .brand-caption {{
        color: var(--accent) !important;
        font-size: .64rem;
        font-weight: 600;
        margin-top: 4px;
        letter-spacing: .18em;
    }}

    .sidebar-user {{
        display: flex;
        align-items: center;
        gap: 11px;
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 11px 12px;
        margin: 4px 0 20px 0;
        box-shadow: var(--shadow);
    }}

    .sidebar-avatar {{
        width: 34px;
        height: 34px;
        flex: 0 0 34px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--sand);
        color: #1D4ED8 !important;
        font-weight: 700;
        font-size: .85rem;
    }}

    
/* ===== SIDEBAR USER - TIMES NEW ROMAN ===== */

.sidebar-user-label {{
    font-family: "Times New Roman", Times, serif !important;
    color: var(--muted) !important;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}}

.sidebar-user-name {{
    font-family: "Times New Roman", Times, serif !important;
    color: var(--ink) !important;
    font-size: 1.1rem;
    font-weight: 600;
    margin-top: 4px;
    overflow-wrap: anywhere;
}}

.sidebar-avatar {{
    font-family: "Times New Roman", Times, serif !important;
    font-weight: 700;
}}


    .sidebar-label {{
        color: var(--muted) !important;
        font-size: .64rem;
        font-weight: 600;
        letter-spacing: .18em;
        margin: 6px 0 8px 4px;
    }}

    .sidebar-foot {{
        color: var(--muted) !important;
        font-size: .68rem;
        line-height: 1.7;
        letter-spacing: .06em;
        border-top: 1px solid var(--line);
        padding-top: 14px;
        margin-top: 8px;
    }}

    .sidebar-foot b {{ color: var(--accent) !important; font-weight: 600; }}

    /* ---------- Page header ---------- */
    .page-eyebrow {{
        display: flex;
        align-items: center;
        gap: 10px;
        color: var(--accent);
        text-transform: uppercase;
        letter-spacing: .2em;
        font-size: .68rem;
        font-weight: 600;
        margin-bottom: .6rem;
    }}

    .page-eyebrow::before {{
        content: "";
        width: 22px;
        height: 2px;
        border-radius: 2px;
        background: var(--accent);
    }}

    .page-title {{
        color: var(--ink);
        font-family: var(--display);
        font-size: clamp(1.9rem, 3vw, 2.5rem);
        font-weight: 600;
        letter-spacing: -.02em;
        line-height: 1.1;
        margin: 0;
    }}

    
.page-subtitle {{
    font-family: "Times New Roman", Times, serif !important;
    color: var(--muted);
    font-size: 1.05rem;
    font-weight: 400;
    line-height: 1.6;
    margin-top: .55rem;
    margin-bottom: 1.6rem;
    max-width: 900px;
}}


    .section-heading {{
        display: flex;
        align-items: baseline;
        gap: 12px;
        color: var(--ink);
        font-family: var(--display);
        font-size: 1.28rem;
        font-weight: 600;
        letter-spacing: -.01em;
        margin: .6rem 0 .25rem 0;
    }}

    /* ---------- Hero ---------- */
    .hero-panel {{
        position: relative;
        overflow: hidden;
        background: {ACCENT_SOFT};
        border-radius: 18px;
        padding: 30px 34px;
        margin: 4px 0 28px 0;
        border: 1px solid #DCE7FB;
        box-shadow: var(--shadow);
    }}

    .hero-panel::after {{
        content: "";
        position: absolute;
        right: -50px;
        top: -70px;
        width: 260px;
        height: 260px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(37,99,235,.10), rgba(37,99,235,0) 70%);
    }}

    .hero-panel::before {{
        content: "";
        position: absolute;
        right: 120px;
        bottom: -90px;
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,.55), rgba(255,255,255,0) 70%);
    }}

    .hero-kicker {{
        position: relative;
        color: var(--accent);
        font-size: .68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: .2em;
    }}

    .hero-title {{
        position: relative;
        color: var(--ink);
        font-family: var(--display);
        font-size: 1.8rem;
        line-height: 1.2;
        font-weight: 500;
        letter-spacing: -.015em;
        margin: 10px 0 8px 0;
    }}

    .hero-title em {{
        font-style: normal;
        color: var(--accent);
    }}

    
.hero-copy {{
    position: relative;
    font-family: "Times New Roman", Times, serif !important;
    color: #475569;
    font-size: 1.05rem;
    font-weight: 400;
    max-width: 900px;
    line-height: 1.65;
}}


    /* ---------- Metric cards ---------- */
    div[data-testid="stMetric"] {{
        background: var(--paper);
        border: 1px solid var(--line);
        border-top: 3px solid var(--accent);
        border-radius: var(--radius);
        padding: 20px 22px 18px 22px;
        min-height: 122px;
        box-shadow: var(--shadow);
        transition: transform .18s ease, box-shadow .18s ease;
    }}

    div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stMetric"],
    div[data-testid="stColumn"]:nth-of-type(4) div[data-testid="stMetric"] {{
        border-top-color: var(--fraud);
    }}

    div[data-testid="stColumn"]:nth-of-type(3) div[data-testid="stMetric"] {{
        border-top-color: var(--safe);
    }}

    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 2px 4px rgba(15,23,42,.04), 0 12px 28px rgba(15,23,42,.07);
    }}

    div[data-testid="stMetricLabel"] p {{
        color: var(--muted) !important;
        font-weight: 600;
        font-size: .74rem;
        text-transform: uppercase;
        letter-spacing: .12em;
    }}

    div[data-testid="stMetricValue"] {{
        color: var(--ink);
        font-family: var(--display);
        font-weight: 600;
        font-size: 2.1rem;
        letter-spacing: -.02em;
        font-variant-numeric: tabular-nums lining-nums;
    }}

    /* ---------- Bordered containers (card) ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"][style*="border"],
    [data-testid="stVerticalBlockBorderWrapper"] > div[style*="border"] {{
        background: var(--paper);
        border-color: var(--line) !important;
        border-radius: var(--radius) !important;
        box-shadow: var(--shadow);
    }}

    /* ---------- Plotly chart frame ---------- */
    [data-testid="stPlotlyChart"] {{
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: var(--radius);
        padding: 6px 6px 0 6px;
        box-shadow: var(--shadow);
    }}

    /* ---------- Status pills ---------- */
    .status-pill {{
        display: inline-block;
        border-radius: 999px;
        padding: 4px 11px;
        font-size: .72rem;
        font-weight: 600;
        letter-spacing: .02em;
    }}
    .status-safe  {{ background: var(--safe-soft);  color: #047857; }}
    .status-fraud {{ background: var(--fraud-soft); color: #E11D48; }}

    /* ---------- Auth ---------- */
    .auth-brand {{
        text-align: center;
        margin: 1.6rem 0 1.4rem 0;
    }}

    .auth-logo {{
        width: 56px;
        height: 56px;
        border-radius: 15px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #3B82F6, {ACCENT_DEEP});
        color: #FFFFFF;
        font-family: var(--display);
        font-size: 1.6rem;
        font-weight: 600;
        margin-bottom: 16px;
        box-shadow: 0 10px 24px rgba(37,99,235,.28);
    }}

    .auth-title {{
        font-family: var(--display);
        font-size: 1.9rem;
        font-weight: 600;
        letter-spacing: -.02em;
        color: var(--ink);
        line-height: 1.1;
    }}

    .auth-subtitle {{
        color: var(--muted);
        font-size: .82rem;
        margin-top: 8px;
        letter-spacing: .14em;
        text-transform: uppercase;
    }}

    .auth-foot {{
        text-align: center;
        color: var(--muted);
        font-size: .72rem;
        letter-spacing: .08em;
        margin-top: 18px;
    }}

    /* Radio ngang trên trang đăng nhập -> segmented control */
    .main [data-testid="stRadio"] [role="radiogroup"] {{
        background: var(--canvas);
        border: 1px solid var(--line);
        border-radius: 11px;
        padding: 4px;
        gap: 4px;
        width: 100%;
    }}

    .main [data-testid="stRadio"] [role="radiogroup"] label {{
        flex: 1;
        justify-content: center;
        border-radius: 8px;
        padding: 7px 10px;
        margin: 0;
        cursor: pointer;
        transition: background .18s ease;
    }}

    .main [data-testid="stRadio"] [role="radiogroup"] label > div:first-child {{
        display: none;
    }}

    .main [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {{
        background: var(--paper);
        box-shadow: 0 1px 3px rgba(15,23,42,.10);
    }}

    .main [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) p {{
        font-weight: 600;
        color: var(--accent-deep);
    }}

    .main [data-testid="stRadio"] [role="radiogroup"] label p {{
        color: var(--muted);
        font-size: .88rem;
    }}

    /* ---------- Buttons ---------- */
    .stButton > button,
    .stFormSubmitButton > button {{
        border-radius: 10px;
        min-height: 2.75rem;
        font-weight: 600;
        letter-spacing: .01em;
        transition: all .18s ease;
    }}

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {{
        background: var(--accent);
        border: 1px solid var(--accent);
        color: #FFFFFF;
        box-shadow: 0 6px 16px rgba(37,99,235,.22);
    }}

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover {{
        background: var(--accent-deep);
        border-color: var(--accent-deep);
        color: #FFFFFF;
        transform: translateY(-1px);
    }}

    .stButton > button[kind="primary"]:focus:not(:active),
    .stFormSubmitButton > button[kind="primary"]:focus:not(:active) {{
        border-color: var(--accent-deep);
        color: #FFFFFF;
    }}

    /* ---------- Inputs ---------- */
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] > div {{
        border-radius: 10px !important;
        background: var(--paper);
    }}

    .stTextInput div[data-baseweb="input"],
    .stNumberInput div[data-baseweb="input"],
    .stSelectbox div[data-baseweb="select"] > div {{
        border-color: var(--line) !important;
        border-radius: 10px !important;
    }}

    .stTextInput div[data-baseweb="input"]:focus-within,
    .stNumberInput div[data-baseweb="input"]:focus-within {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,.15);
    }}

    .stTextInput label p, .stSelectbox label p, .stNumberInput label p {{
        font-size: .8rem;
        font-weight: 600;
        color: #334155 !important;
        letter-spacing: .01em;
    }}

    [data-testid="stForm"] {{
        border: none;
        padding: 0;
    }}

    /* ---------- Dataframe ---------- */
    div[data-testid="stDataFrame"] {{
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: var(--radius);
        overflow: hidden;
        box-shadow: var(--shadow);
    }}

    /* ---------- Alerts ---------- */
    [data-testid="stAlert"] {{ border-radius: 12px; }}

    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
        .hero-panel {{ padding: 24px 22px; }}
        .hero-title {{ font-size: 1.45rem; }}
    }}
    /* FIX: Streamlit Material Icons */

.material-symbols-rounded,
.material-symbols-outlined,
.material-icons {{
    font-family: "Material Symbols Rounded" !important;
    font-weight: normal !important;
    font-style: normal !important;
    font-size: 24px !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    direction: ltr;
    font-feature-settings: "liga" !important;
    -webkit-font-feature-settings: "liga" !important;
}}

/* Đồng bộ font cho các thành phần văn bản tùy chỉnh */

.page-title,
.page-subtitle,
.hero-title,
.hero-copy,
.section-heading,
.pd-section,
.pd-caption,
.pd-step,
.pd-result-label,
.pd-result-value,
.pd-result-desc,
.pd-kpi-label,
.pd-kpi-value,
.pd-kpi-sub,
.pd-gauge-head,
.pd-legend,
.pd-detail-label,
.pd-detail-value,
.pd-footer {{
    font-family: "Times New Roman", Times, serif !important;
}}

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. SESSION STATE
# =========================================================
DEFAULT_STATE = {
    "access_token": None,
    "current_user": None,
    "selected_page": "Dashboard",
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# 4. SHARED UI HELPERS
# =========================================================
def esc(value) -> str:
    """Escape giá trị trước khi chèn vào HTML (tránh lỗi hiển thị / XSS từ username)."""
    return html.escape(str(value or ""))


def page_header(eyebrow: str, title: str, subtitle: str):
    eyebrow_html = f'<div class="page-eyebrow">{eyebrow}</div>' if eyebrow else ""
    st.markdown(
        f"""
        {eyebrow_html}
        <div class="page-title">{title}</div>
        <div class="page-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, caption: str = ""):
    st.markdown(f'<div class="section-heading">{title}</div>', unsafe_allow_html=True)
    if caption:
        st.caption(caption)


def configure_plotly(fig, height=360):
    """Ngôn ngữ hình ảnh chung cho biểu đồ — tông Modern Blue."""
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=58, b=24),
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font=dict(family=FONT_SANS, color=TEXT_SOFT, size=12),
        title=dict(
            font=dict(size=17, color=INK, family=FONT_DISPLAY),
            x=0.03,
            xanchor="left",
            y=0.95,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text="",
            font=dict(size=11, color=TEXT_SOFT),
        ),
        hoverlabel=dict(
            bgcolor=INK,
            bordercolor=INK,
            font=dict(color="#FFFFFF", family=FONT_SANS, size=12),
        ),
        bargap=0.45,
        uniformtext_minsize=10,
        uniformtext_mode="hide",
    )
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor=LINE,
        linewidth=1,
        ticks="",
        tickfont=dict(size=12, color=TEXT_SOFT),
        title_font=dict(size=11, color=MUTED),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=LINE_SOFT,
        gridwidth=1,
        griddash="dot",
        zeroline=False,
        showline=False,
        ticks="",
        tickfont=dict(size=11, color=MUTED),
        title_font=dict(size=11, color=MUTED),
    )
    return fig


def safe_number(data, key, default=0):
    try:
        return float(data.get(key, default) or default)
    except (TypeError, ValueError, AttributeError):
        return default


def logout():
    st.session_state.access_token = None
    st.session_state.current_user = None
    st.session_state.selected_page = "Dashboard"
    st.rerun()


# =========================================================
# 5. AUTHENTICATION
# =========================================================
def login_page():
    left, center, right = st.columns([1, 1.15, 1])

    with center:
        st.markdown(
            """
            <div class="auth-brand">
                <div class="auth-logo">B</div>
                <div class="auth-title">BankSim Intelligence</div>
                <div class="auth-subtitle">Fraud detection · Machine Learning</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            auth_mode = st.radio(
                "Tài khoản",
                ["Đăng nhập", "Tạo tài khoản"],
                horizontal=True,
                label_visibility="collapsed",
            )

            if auth_mode == "Đăng nhập":
                st.markdown("### Chào mừng trở lại")
                st.caption("Đăng nhập để tiếp tục giám sát và phân tích giao dịch.")

                with st.form("login_form", clear_on_submit=False):
                    username = st.text_input(
                        "Tên đăng nhập",
                        placeholder="Nhập tên đăng nhập",
                    )
                    password = st.text_input(
                        "Mật khẩu",
                        type="password",
                        placeholder="Nhập mật khẩu",
                    )
                    submitted = st.form_submit_button(
                        "Đăng nhập",
                        type="primary",
                        use_container_width=True,
                    )

                if submitted:
                    if not username.strip() or not password:
                        st.warning("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
                    else:
                        with st.spinner("Đang xác thực tài khoản..."):
                            result = login_user(username.strip(), password)

                        if result and "access_token" in result:
                            token = result["access_token"]
                            user = get_current_user(token)

                            if user:
                                st.session_state.access_token = token
                                st.session_state.current_user = user
                                st.session_state.selected_page = "Dashboard"
                                st.rerun()
                            else:
                                st.error("Đăng nhập thành công nhưng không thể tải thông tin người dùng.")
                        elif result and "error" in result:
                            st.error(result["error"])
                        else:
                            st.error("Đăng nhập thất bại. Vui lòng thử lại.")

            else:
                st.markdown("### Tạo tài khoản")
                st.caption("Tạo tài khoản để lưu và theo dõi lịch sử phân tích của bạn.")

                with st.form("register_form", clear_on_submit=False):
                    new_username = st.text_input(
                        "Tên đăng nhập",
                        placeholder="Ví dụ: nguyenvana",
                    )
                    new_email = st.text_input(
                        "Email",
                        placeholder="name@example.com",
                    )
                    new_password = st.text_input(
                        "Mật khẩu",
                        type="password",
                        placeholder="Tạo mật khẩu",
                    )
                    confirm_password = st.text_input(
                        "Xác nhận mật khẩu",
                        type="password",
                        placeholder="Nhập lại mật khẩu",
                    )
                    submitted = st.form_submit_button(
                        "Tạo tài khoản",
                        type="primary",
                        use_container_width=True,
                    )

                if submitted:
                    if not all([new_username.strip(), new_email.strip(), new_password, confirm_password]):
                        st.warning("Vui lòng điền đầy đủ thông tin.")
                    elif new_password != confirm_password:
                        st.error("Mật khẩu xác nhận không khớp.")
                    else:
                        with st.spinner("Đang tạo tài khoản..."):
                            result = register_user(
                                username=new_username.strip(),
                                email=new_email.strip(),
                                password=new_password,
                            )

                        if result and "error" in result:
                            st.error(result["error"])
                        elif result:
                            st.success("Tạo tài khoản thành công. Hãy chuyển sang Đăng nhập.")
                        else:
                            st.error("Không nhận được phản hồi từ Backend.")

        st.markdown(
            '<div class="auth-foot">BankSim · XGBoost · Bảo mật phiên làm việc</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# 6. DASHBOARD
# =========================================================
def build_history_dataframe(history):
    rows = []

    if not isinstance(history, list):
        return pd.DataFrame()

    for item in history:
        if not isinstance(item, dict):
            continue

        transaction = item.get("transaction", {})
        if not isinstance(transaction, dict):
            continue

        probability = safe_number(item, "fraud_probability", 0) * 100
        predicted_label = item.get("predicted_label", 0)

        rows.append(
            {
                "ID": transaction.get("id"),
                "Thời gian": transaction.get("created_at"),
                "Nhóm tuổi": transaction.get("age"),
                "Giới tính": transaction.get("gender"),
                "Số tiền": safe_number(transaction, "amount"),
                "Merchant": transaction.get("merchant"),
                "Danh mục": transaction.get("category"),
                "Nguồn": transaction.get("source"),
                "Xác suất gian lận (%)": probability,
                "Kết quả": "Gian lận" if predicted_label == 1 else "Bình thường",
            }
        )

    df = pd.DataFrame(rows)
    if not df.empty and "ID" in df.columns:
        df = df.sort_values(by="ID", ascending=False, na_position="last")
    return df


def dashboard_page():
    user = st.session_state.current_user or {}
    token = st.session_state.access_token
    username = esc(user.get("username", "User"))

    page_header(
        "",
        "Tổng quan hệ thống",
        "Theo dõi hoạt động giao dịch và kết quả phát hiện gian lận của tài khoản.",
    )

    st.markdown(
        f"""
        <div class="hero-panel">
            <div class="hero-title">Xin chào, <em>{username}</em></div>
            <div class="hero-copy">
                Theo dõi giao dịch, nhận diện dấu hiệu bất thường và quản lý
                kết quả phân tích trên một giao diện tập trung.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Đang đồng bộ dữ liệu giao dịch..."):
        statistics = get_statistics(token)
        history = get_transaction_history(token)

    if isinstance(statistics, dict) and "error" in statistics:
        st.error(statistics["error"])
        return

    if isinstance(history, dict) and "error" in history:
        st.error(history["error"])
        return

    if not isinstance(statistics, dict):
        st.error("Dữ liệu thống kê từ Backend không hợp lệ.")
        return

    total = int(safe_number(statistics, "total_transactions"))
    fraud = int(safe_number(statistics, "fraud_transactions"))
    normal = int(safe_number(statistics, "normal_transactions"))
    fraud_rate = safe_number(statistics, "fraud_rate")

    section_title("Chỉ số giao dịch", "Các chỉ số được tổng hợp từ dữ liệu giao dịch của tài khoản.")

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    c1.metric("Tổng giao dịch", f"{total:,}", help="Tổng số giao dịch đã được ghi nhận.")
    c2.metric("Giao dịch gian lận", f"{fraud:,}", help="Số giao dịch được mô hình phân loại là gian lận.")
    c3.metric("Giao dịch bình thường", f"{normal:,}", help="Số giao dịch được mô hình phân loại là bình thường.")
    c4.metric("Tỷ lệ gian lận", f"{fraud_rate:.2f}%", help="Tỷ lệ giao dịch được phân loại là gian lận.")

    st.write("")
    section_title("Phân tích giao dịch", "Tương quan giữa giao dịch gian lận và giao dịch bình thường.")

    chart_data = pd.DataFrame(
        {
            "Loại giao dịch": ["Gian lận", "Bình thường"],
            "Số lượng": [fraud, normal],
        }
    )

    chart_left, chart_right = st.columns([1, 1.35], gap="medium")

    with chart_left:
        fig_donut = px.pie(
            chart_data,
            names="Loại giao dịch",
            values="Số lượng",
            hole=0.78,
            color="Loại giao dịch",
            color_discrete_map={
                "Gian lận": FRAUD,
                "Bình thường": SAFE,
            },
        )
        fig_donut.update_traces(
            textposition="outside",
            texttemplate="%{percent:.1%}",
            textfont=dict(size=12, color=TEXT_SOFT, family=FONT_SANS),
            marker=dict(line=dict(color=PAPER, width=4)),
            sort=False,
            hovertemplate="<b>%{label}</b><br>Số lượng: %{value:,}<br>Tỷ lệ: %{percent}<extra></extra>",
        )
        fig_donut = configure_plotly(fig_donut, height=370)
        fig_donut.update_layout(
            title="Cơ cấu phân loại",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.04,
                xanchor="center",
                x=0.5,
                title_text="",
                font=dict(size=11, color=TEXT_SOFT),
            ),
            margin=dict(l=24, r=24, t=58, b=48),
            annotations=[
                dict(
                    text=(
                        f"<b>{total:,}</b><br>"
                        f"<span style='font-size:10px;color:{MUTED};"
                        f"font-family:Times New Roman;letter-spacing:2px'>GIAO DỊCH</span>"
                    ),
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=28, color=INK, family=FONT_DISPLAY),
                )
            ],
        )
        st.plotly_chart(
            fig_donut,
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )

    with chart_right:
        fig_bar = go.Figure()
        bar_colors = [FRAUD, SAFE]
        for label, value, color in zip(
            chart_data["Loại giao dịch"],
            chart_data["Số lượng"],
            bar_colors,
        ):
            fig_bar.add_trace(
                go.Bar(
                    x=[label],
                    y=[value],
                    name=label,
                    width=0.42,
                    marker=dict(
                        color=color,
                        line=dict(width=0),
                        cornerradius=6,
                    ),
                    text=[f"{value:,}"],
                    textposition="outside",
                    textfont=dict(size=14, color=INK, family=FONT_DISPLAY),
                    hovertemplate="<b>%{x}</b><br>Số lượng: %{y:,}<extra></extra>",
                    cliponaxis=False,
                )
            )
        fig_bar.update_layout(
            title="Số lượng theo phân loại",
            showlegend=False,
            barmode="group",
            yaxis=dict(
                rangemode="tozero",
                range=[0, max(max(fraud, normal) * 1.2, 1)],
                title="Số giao dịch",
            ),
            xaxis=dict(title=None),
        )
        fig_bar = configure_plotly(fig_bar, height=370)
        fig_bar.update_layout(
            margin=dict(l=20, r=24, t=58, b=38),
            showlegend=False,
        )
        st.plotly_chart(
            fig_bar,
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )

    st.write("")
    section_title("Giao dịch gần đây", "Các giao dịch mới nhất được lưu trong hệ thống.")

    history_df = build_history_dataframe(history)

    if history_df.empty:
        st.info("Chưa có giao dịch nào được ghi nhận. Hãy tạo giao dịch tại mục Dự đoán giao dịch.")
        return

    filter_col, search_col = st.columns([1, 2], gap="medium")
    with filter_col:
        selected_result = st.selectbox(
            "Trạng thái",
            ["Tất cả", "Gian lận", "Bình thường"],
        )
    with search_col:
        search_text = st.text_input(
            "Tìm kiếm",
            placeholder="Tìm theo Merchant hoặc danh mục giao dịch...",
        )

    filtered_df = history_df.copy()

    if selected_result != "Tất cả":
        filtered_df = filtered_df[
            filtered_df["Kết quả"].str.endswith(selected_result, na=False)
        ]

    if search_text.strip():
        search_mask = (
            filtered_df["Merchant"].astype(str).str.contains(search_text, case=False, na=False, regex=False)
            | filtered_df["Danh mục"].astype(str).str.contains(search_text, case=False, na=False, regex=False)
        )
        filtered_df = filtered_df[search_mask]

    if "Thời gian" in filtered_df.columns:
        filtered_df["Thời gian"] = pd.to_datetime(
            filtered_df["Thời gian"], errors="coerce"
        ).dt.strftime("%d/%m/%Y %H:%M")

    st.caption(f"Hiển thị {len(filtered_df):,} / {len(history_df):,} giao dịch")

    
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=520,
        column_order=[
            "Thời gian",
            "Nhóm tuổi",
            "Giới tính",
            "Số tiền",
            "Merchant",
            "Danh mục",
            "Xác suất gian lận (%)",
            "Kết quả",
            "ID",
        ],
        column_config={
            "Thời gian": st.column_config.TextColumn(
                "Thời gian", width=170
            ),
            "Nhóm tuổi": st.column_config.TextColumn(
                "Nhóm tuổi", width=100
            ),
            "Giới tính": st.column_config.TextColumn(
                "Giới tính", width=90
            ),
            "Số tiền": st.column_config.NumberColumn(
                "Số tiền", width=110, format="%.2f"
            ),
            "Merchant": st.column_config.TextColumn(
                "Merchant", width=120
            ),
            "Danh mục": st.column_config.TextColumn(
                "Danh mục", width=180
            ),
            "Nguồn": st.column_config.TextColumn(
                "Nguồn", width=100
            ),
            "Xác suất gian lận (%)": st.column_config.NumberColumn(
                "Mức độ rủi ro",
                format="%.2f%%",
                width=100,
            ),
            "Kết quả": st.column_config.TextColumn(
                "Kết quả", width=130
            ),
            "ID": st.column_config.NumberColumn(
                "Mã GD", width=80, format="%d"
            ),
        },
    )


# =========================================================
# 7. MAIN APPLICATION
# =========================================================
NAV_LABELS = {
    "Dashboard": "Tổng quan",
    "Dự đoán giao dịch": "Dự đoán giao dịch",
}


def render_sidebar():
    user = st.session_state.current_user or {}
    raw_name = str(user.get("username", "User") or "User")
    username = esc(raw_name)
    initial = esc(raw_name[:1].upper() or "U")

    with st.sidebar:
        st.markdown(
            """
            <div class="brand-lockup">
                <div class="brand-mark">B</div>
                <div>
                    <div class="brand-name">BankSim</div>
                    <div class="brand-caption">FRAUD INTELLIGENCE</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="sidebar-user">
                <div class="sidebar-avatar">{initial}</div>
                <div>
                    <div class="sidebar-user-label">Tài khoản</div>
                    <div class="sidebar-user-name">{username}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-label">WORKSPACE</div>', unsafe_allow_html=True)

        selected_page = st.radio(
            "Điều hướng",
            options=list(NAV_LABELS.keys()),
            format_func=lambda x: NAV_LABELS.get(x, x),
            key="selected_page",
            label_visibility="collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Đăng xuất", use_container_width=True):
            logout()

        st.markdown(
            '<div class="sidebar-foot">AI-POWERED FRAUD DETECTION<br>'
            '<b>BankSim</b> · XGBoost</div>',
            unsafe_allow_html=True,
        )

    return selected_page


def main():
    if not st.session_state.access_token:
        login_page()
        return

    selected_page = render_sidebar()

    if selected_page == "Dashboard":
        dashboard_page()
    elif selected_page == "Dự đoán giao dịch":
        page_header(
            "",
            "Phân tích giao dịch",
            "Nhập thông tin giao dịch để hệ thống đánh giá nguy cơ gian lận.",
        )
        predict_page()


if __name__ == "__main__":
    main()