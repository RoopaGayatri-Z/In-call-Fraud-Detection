import json
from pathlib import Path

import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Fraud Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DEMO_DIR = BASE_DIR / "Demo"

# ------------------------------------------------------------
# IMPORTANT:
# The backend is NOT connected yet.
# Therefore the risk score below is DEMO DATA only.
# When the backend is connected, this section will be replaced
# by the real RiskScoreResponse from the FastAPI backend.
# ------------------------------------------------------------

DEMO_MODE = True


# ============================================================
# LOAD DEMO SCRIPT
# ============================================================

def load_demo_script(call_type):
    if call_type == "Suspicious bank caller":
        file_path = DEMO_DIR / "scam_call_script.json"
    else:
        file_path = DEMO_DIR / "normal_call_script.json"

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# DEMO RISK DATA
# ============================================================

def get_demo_risk(call_type):
    """
    Temporary frontend-only data.

    This is NOT AI-generated and is NOT coming from the backend.
    It exists only so the UI can be demonstrated before the
    FastAPI backend is connected.
    """

    if call_type == "Suspicious bank caller":
        return {
            "risk_score": 0.78,
            "should_warn": True,
            "signals": [
                (
                    "🚨 Urgency",
                    "Caller is creating pressure to act immediately.",
                ),
                (
                    "🔒 Secrecy / Isolation",
                    "Caller instructed the user not to tell family members.",
                ),
                (
                    "🏦 Authority Impersonation",
                    "Caller claims to be from the user's bank.",
                ),
                (
                    "🔐 Credential Request",
                    "Caller requested an OTP for verification.",
                ),
            ],
            "reasoning": (
                "The conversation contains multiple high-risk indicators. "
                "The caller is impersonating a bank representative, creating "
                "urgency, instructing the user to keep the conversation secret, "
                "and requesting an OTP. These patterns strongly suggest a "
                "potential financial scam."
            ),
        }

    return {
        "risk_score": 0.12,
        "should_warn": False,
        "signals": [],
        "reasoning": (
            "The conversation does not currently contain strong indicators "
            "of fraud. The interaction appears to be a normal family call."
        ),
    }


# ============================================================
# SESSION STATE
# ============================================================

if "call_started" not in st.session_state:
    st.session_state.call_started = False

if "script" not in st.session_state:
    st.session_state.script = []

if "call_type" not in st.session_state:
    st.session_state.call_type = "Suspicious bank caller"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* =========================
       MAIN BACKGROUND
       ========================= */

    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(22, 115, 79, 0.20),
                transparent 35%
            ),
            linear-gradient(
                135deg,
                #021812 0%,
                #03271c 50%,
                #01150f 100%
            );
        color: #f4f7f5;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* =========================
       HIDE STREAMLIT ELEMENTS
       ========================= */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* =========================
       SIDEBAR
       ========================= */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #02261b,
                #011a12
            );
        border-right: 1px solid #14563d;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    .sidebar-title {
        text-align: center;
        font-size: 25px;
        font-weight: 800;
        color: #f4f7f5;
        margin-top: 5px;
    }

    .sidebar-subtitle {
        text-align: center;
        color: #65dda0;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 5px;
    }

    .sidebar-icon {
        text-align: center;
        font-size: 48px;
        margin-bottom: 5px;
    }

    .sidebar-heading {
        color: #62dda0;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.2px;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .sidebar-box {
        background: rgba(5, 57, 40, 0.7);
        border: 1px solid #176344;
        border-radius: 12px;
        padding: 13px;
        margin-top: 10px;
    }

    .sidebar-box-title {
        color: #f0f5f2;
        font-weight: 700;
        font-size: 13px;
    }

    .sidebar-box-text {
        color: #91afa1;
        font-size: 11px;
        line-height: 1.6;
        margin-top: 5px;
    }

    /* =========================
       HEADER
       ========================= */

    .main-title {
        font-family: Georgia, serif;
        font-size: 38px;
        font-weight: 800;
        color: #f4f6f5;
        margin-bottom: 0;
    }

    .main-subtitle {
        color: #62dda0;
        font-size: 15px;
        margin-top: 3px;
    }

    .system-active {
        text-align: right;
        margin-top: 10px;
    }

    .system-badge {
        display: inline-block;
        border: 1px solid #176b4a;
        background: rgba(5, 54, 38, 0.7);
        border-radius: 25px;
        padding: 8px 15px;
        color: #cfe8db;
        font-size: 12px;
    }

    .green-dot {
        color: #32e783;
    }

    h1, h2, h3 {
        color: #f4f7f5 !important;
    }

    /* =========================
       CARDS
       ========================= */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background:
            linear-gradient(
                145deg,
                rgba(6, 48, 34, 0.96),
                rgba(3, 34, 24, 0.96)
            );
        border: 1px solid #155b40 !important;
        border-radius: 15px !important;
    }

    /* =========================
       BUTTONS
       ========================= */

    .stButton > button {
        border-radius: 8px;
        min-height: 42px;
        font-weight: 700;
        border: 1px solid #1b7652;
        background: #073326;
        color: #e6f2ec;
    }

    .stButton > button:hover {
        border-color: #38e58b;
        color: white;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(
            135deg,
            #1eb86a,
            #159b59
        ) !important;
        border: 1px solid #42e78d !important;
        color: white !important;
    }

    /* =========================
       SELECTBOX
       ========================= */

    label {
        color: #91afa1 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #06251a !important;
        border: 1px solid #176344 !important;
        border-radius: 8px !important;
    }

    /* =========================
       TRANSCRIPT
       ========================= */

    .transcript-box {
        background: rgba(1, 24, 17, 0.65);
        border: 1px dashed #19704e;
        border-radius: 12px;
        padding: 15px;
    }

    .message {
        background: rgba(8, 52, 37, 0.75);
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
        border-left: 3px solid #20ca72;
    }

    .caller {
        color: #72e3a7;
        font-weight: 700;
    }

    .user {
        color: #8eb7ff;
        font-weight: 700;
    }

    .message-text {
        color: #d4e3db;
        font-size: 14px;
        line-height: 1.5;
    }

    .empty {
        text-align: center;
        padding: 35px 10px;
        color: #719688;
        font-style: italic;
    }

    /* =========================
       RISK
       ========================= */

    .risk-number {
        text-align: center;
        font-size: 45px;
        font-weight: 800;
        color: white;
    }

    .high-risk {
        text-align: center;
        color: #ff6862;
        font-weight: 800;
    }

    .low-risk {
        text-align: center;
        color: #58df96;
        font-weight: 800;
    }

    .awaiting {
        text-align: center;
        color: #829e91;
        font-weight: 700;
    }

    .demo-note {
        text-align: center;
        color: #dcb34b;
        font-size: 11px;
        margin-top: 8px;
    }

    /* =========================
       SIGNALS
       ========================= */

    .signal {
        background: rgba(7, 51, 36, 0.8);
        border: 1px solid #196447;
        border-left: 4px solid #2bd77c;
        border-radius: 9px;
        padding: 12px;
        margin-bottom: 9px;
    }

    .signal-title {
        color: #edf5f0;
        font-weight: 700;
    }

    .signal-text {
        color: #91aa9e;
        font-size: 12px;
        margin-top: 5px;
        line-height: 1.5;
    }

    /* =========================
       AI ASSESSMENT
       ========================= */

    .ai-badge {
        display: inline-block;
        border: 1px solid #217a54;
        border-radius: 20px;
        padding: 5px 12px;
        color: #8ce6b3;
        font-size: 12px;
    }

    /* =========================
       FOOTER
       ========================= */

    .footer {
        text-align: center;
        color: #62d998;
        font-size: 12px;
        padding: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-icon">🛡️</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-title">Fraud Guardian</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-subtitle">Real-time in-call<br>fraud intelligence</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-heading">NAVIGATION</div>',
        unsafe_allow_html=True,
    )

    st.button("📞  Call Monitor", use_container_width=True)
    st.button("◷  Risk History", use_container_width=True)
    st.button("⚙️  Settings", use_container_width=True)

    st.divider()

    st.markdown(
        '<div class="sidebar-heading">SYSTEM STATUS</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-box"><div class="sidebar-box-title">🟢 System active</div><div class="sidebar-box-text">Frontend demo is running. Backend connection is pending.</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-box"><div class="sidebar-box-title">🛡️ About</div><div class="sidebar-box-text">Fraud Guardian is designed to detect suspicious patterns in real-time phone conversations.</div></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns([4, 1])

with header_left:

    st.markdown(
        '<div class="main-title">Fraud Guardian</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">Real-time in-call fraud intelligence</div>',
        unsafe_allow_html=True,
    )

with header_right:

    st.markdown(
        '<div class="system-active"><span class="system-badge"><span class="green-dot">●</span> System active</span></div>',
        unsafe_allow_html=True,
    )

st.divider()


# ============================================================
# CALL CONTROL
# ============================================================

with st.container(border=True):

    st.subheader("☎  Call control")

    col1, col2, col3, col4 = st.columns([2.5, 1.5, 1.1, 1])

    with col1:

        call_type = st.selectbox(
            "Scenario",
            [
                "Suspicious bank caller",
                "Normal family call",
            ],
        )

    with col2:

        if st.session_state.call_started:
            st.write("🟢 Call in progress")
        else:
            st.write("No active call")

    with col3:

        start_call = st.button(
            "▶ Start call",
            use_container_width=True,
            type="primary",
        )

    with col4:

        stop_call = st.button(
            "■ Stop",
            use_container_width=True,
        )


# ============================================================
# CALL ACTIONS
# ============================================================

if start_call:

    try:
        st.session_state.script = load_demo_script(call_type)
        st.session_state.call_type = call_type
        st.session_state.call_started = True

    except FileNotFoundError:

        st.session_state.call_started = False
        st.session_state.script = []

        st.error(
            f"Demo file not found in: {DEMO_DIR}\n\n"
            "Make sure the Demo folder contains the two JSON files."
        )


if stop_call:

    st.session_state.call_started = False
    st.session_state.script = []


st.write("")


# ============================================================
# TRANSCRIPT + RISK
# ============================================================

left, right = st.columns([1.35, 1])


# ============================================================
# TRANSCRIPT
# ============================================================

with left:

    with st.container(border=True):

        st.subheader("▣  Live transcript")

        if st.session_state.call_started:

            st.markdown(
                '<div class="transcript-box">',
                unsafe_allow_html=True,
            )

            for chunk in st.session_state.script:

                if chunk["speaker"] == "caller":

                    st.markdown(
                        f'<div class="message"><span class="caller">🔴 Caller</span><br><span class="message-text">{chunk["text"]}</span></div>',
                        unsafe_allow_html=True,
                    )

                else:

                    st.markdown(
                        f'<div class="message"><span class="user">🔵 You</span><br><span class="message-text">{chunk["text"]}</span></div>',
                        unsafe_allow_html=True,
                    )

            st.markdown(
                '</div>',
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                '<div class="empty">🎙️<br><br>Start a call to begin real-time monitoring.</div>',
                unsafe_allow_html=True,
            )


# ============================================================
# FRAUD RISK
# ============================================================

with right:

    with st.container(border=True):

        st.subheader("♢  Fraud risk")

        if st.session_state.call_started:

            # ------------------------------------------------
            # TEMPORARY FRONTEND DEMO
            # ------------------------------------------------
            # This 78% / 12% value is NOT produced by AI.
            # It is temporary data for demonstrating the UI.
            # ------------------------------------------------

            if DEMO_MODE:
                risk_data = get_demo_risk(st.session_state.call_type)
                risk = risk_data["risk_score"]
                should_warn = risk_data["should_warn"]

                st.markdown(
                    f'<div class="risk-number">{risk * 100:.0f}%</div>',
                    unsafe_allow_html=True,
                )

                if should_warn:

                    st.markdown(
                        '<div class="high-risk">🔴 HIGH RISK</div>',
                        unsafe_allow_html=True,
                    )

                    st.progress(risk)

                    st.caption("High-risk behavior detected")

                else:

                    st.markdown(
                        '<div class="low-risk">🟢 LOW RISK</div>',
                        unsafe_allow_html=True,
                    )

                    st.progress(risk)

                    st.caption("No significant fraud indicators")

                st.markdown(
                    '<div class="demo-note">Demo score — backend not connected</div>',
                    unsafe_allow_html=True,
                )

        else:

            st.markdown(
                '<div class="risk-number">--%</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="awaiting">Awaiting call</div>',
                unsafe_allow_html=True,
            )

            st.progress(0)

            st.caption("🟢 Awaiting call")


st.write("")


# ============================================================
# DETECTED SIGNALS
# ============================================================

with st.container(border=True):

    st.subheader("⌕  Detected fraud signals")

    if st.session_state.call_started:

        if DEMO_MODE:

            risk_data = get_demo_risk(st.session_state.call_type)
            signals = risk_data["signals"]

            if signals:

                col1, col2 = st.columns(2)

                for i, (title, description) in enumerate(signals):

                    target = col1 if i % 2 == 0 else col2

                    with target:

                        st.markdown(
                            f'<div class="signal"><div class="signal-title">{title}</div><div class="signal-text">{description}</div></div>',
                            unsafe_allow_html=True,
                        )

            else:

                st.info("🛡️ No suspicious signals detected.")

    else:

        st.info("🛡️ Start a call to detect fraud signals.")


st.write("")


# ============================================================
# AI ASSESSMENT
# ============================================================

with st.container(border=True):

    st.subheader("☆  AI risk assessment")

    if st.session_state.call_started:

        if DEMO_MODE:

            risk_data = get_demo_risk(st.session_state.call_type)

            if risk_data["should_warn"]:

                st.markdown(
                    '<span class="ai-badge">High-risk conversation</span>',
                    unsafe_allow_html=True,
                )

            else:

                st.markdown(
                    '<span class="ai-badge">Low-risk conversation</span>',
                    unsafe_allow_html=True,
                )

            st.write("")

            st.write(risk_data["reasoning"])

            st.caption(
                "Demo assessment — real AI assessment will come from the backend."
            )

    else:

        st.markdown(
            '<span class="ai-badge">Awaiting call</span>',
            unsafe_allow_html=True,
        )

        st.write("")

        st.write(
            "An assessment will appear once a call is being monitored."
        )


# ============================================================
# FRAUD WARNING
# ============================================================

if st.session_state.call_started:

    if DEMO_MODE:

        risk_data = get_demo_risk(st.session_state.call_type)

        if risk_data["should_warn"]:

            st.write("")

            # Native Streamlit components are intentionally used here.
            # This avoids the HTML-tags-being-displayed problem.

            with st.container(border=True):

                st.error("🚨 POSSIBLE FRAUD DETECTED")

                st.markdown(
                    "**This conversation contains suspicious behavior.**"
                )

                st.markdown(
                    "**Do not share OTPs, PINs, passwords, "
                    "or banking details.**"
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">🛡️ Fraud Guardian &nbsp;•&nbsp; Protecting you from fraud, in real time.</div>',
    unsafe_allow_html=True,
)
