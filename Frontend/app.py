import html
import json
import time
from pathlib import Path

import streamlit as st
import websocket


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


# ============================================================
# BACKEND
# ============================================================

BACKEND_WS_URL = "ws://127.0.0.1:8000/ws/assess-call"

# Delay between transcript turns.
# Lower this if you want a faster demonstration.
CHUNK_DELAY = 1.5


# ============================================================
# LOAD DEMO SCRIPT
# ============================================================

def load_demo_script(call_type):

    if call_type == "Suspicious bank caller":
        file_path = DEMO_DIR / "scam_call_script.json"
    else:
        file_path = DEMO_DIR / "normal_call_script.json"

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "call_started": False,
    "call_running": False,
    "session_id": None,
    "script": [],
    "visible_transcript": [],
    "call_type": "Suspicious bank caller",
    "risk_data": None,
    "backend_error": None,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* =========================================================
   MAIN BACKGROUND
   ========================================================= */

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


/* =========================================================
   HIDE STREAMLIT ELEMENTS
   ========================================================= */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

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


/* =========================================================
   HEADER
   ========================================================= */

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

h1,
h2,
h3 {
    color: #f4f7f5 !important;
}


/* =========================================================
   CARDS
   ========================================================= */

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


/* =========================================================
   BUTTONS
   ========================================================= */

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
    background:
        linear-gradient(
            135deg,
            #1eb86a,
            #159b59
        ) !important;

    border: 1px solid #42e78d !important;
    color: white !important;
}


/* =========================================================
   SELECTBOX
   ========================================================= */

label {
    color: #91afa1 !important;
}

div[data-baseweb="select"] > div {
    background-color: #06251a !important;
    border: 1px solid #176344 !important;
    border-radius: 8px !important;
}


/* =========================================================
   TRANSCRIPT
   ========================================================= */

.transcript-box {
    background: rgba(1, 24, 17, 0.65);
    border: 1px dashed #19704e;
    border-radius: 12px;
    padding: 15px;
    max-height: 620px;
    overflow-y: auto;
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


/* =========================================================
   RISK
   ========================================================= */

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

.live-status {
    text-align: center;
    color: #62dda0;
    font-size: 11px;
    font-weight: 700;
    margin-top: 8px;
}


/* =========================================================
   SIGNALS
   ========================================================= */

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


/* =========================================================
   AI ASSESSMENT
   ========================================================= */

.ai-badge {
    display: inline-block;
    border: 1px solid #217a54;
    border-radius: 20px;
    padding: 5px 12px;
    color: #8ce6b3;
    font-size: 12px;
}


/* =========================================================
   FOOTER
   ========================================================= */

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
        '<div class="sidebar-subtitle">'
        'Real-time in-call<br>fraud intelligence'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-heading">NAVIGATION</div>',
        unsafe_allow_html=True,
    )

    st.button(
        "📞  Call Monitor",
        use_container_width=True,
    )

    st.button(
        "◷  Risk History",
        use_container_width=True,
    )

    st.button(
        "⚙️  Settings",
        use_container_width=True,
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-heading">SYSTEM STATUS</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-box">'
        '<div class="sidebar-box-title">'
        '🟢 System active'
        '</div>'
        '<div class="sidebar-box-text">'
        'FastAPI backend and AI risk assessment are connected.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-box">'
        '<div class="sidebar-box-title">'
        '🛡️ About'
        '</div>'
        '<div class="sidebar-box-text">'
        'Fraud Guardian detects suspicious patterns '
        'in real-time phone conversations.'
        '</div>'
        '</div>',
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
        '<div class="main-subtitle">'
        'Real-time in-call fraud intelligence'
        '</div>',
        unsafe_allow_html=True,
    )


with header_right:

    st.markdown(
        '<div class="system-active">'
        '<span class="system-badge">'
        '<span class="green-dot">●</span> System active'
        '</span>'
        '</div>',
        unsafe_allow_html=True,
    )


st.divider()


# ============================================================
# CALL CONTROL
# ============================================================

with st.container(border=True):

    st.subheader("☎  Call control")

    col1, col2, col3, col4 = st.columns(
        [2.5, 1.5, 1.1, 1]
    )

    with col1:

        call_type = st.selectbox(
            "Scenario",
            [
                "Suspicious bank caller",
                "Normal family call",
            ],
            disabled=st.session_state.call_running,
        )

    with col2:

        if st.session_state.call_running:

            st.write("🔴 Call in progress")

        elif st.session_state.call_started:

            st.write("🟢 Call completed")

        else:

            st.write("No active call")

    with col3:

        start_call = st.button(
            "▶ Start call",
            use_container_width=True,
            type="primary",
            disabled=st.session_state.call_running,
        )

    with col4:

        stop_call = st.button(
            "■ Stop",
            use_container_width=True,
        )


# ============================================================
# STOP CALL
# ============================================================

if stop_call:

    st.session_state.call_started = False
    st.session_state.call_running = False
    st.session_state.session_id = None
    st.session_state.script = []
    st.session_state.visible_transcript = []
    st.session_state.risk_data = None
    st.session_state.backend_error = None

    st.rerun()


# ============================================================
# MAIN DASHBOARD PLACEHOLDERS
# ============================================================

left, right = st.columns(
    [1.35, 1]
)


# ============================================================
# TRANSCRIPT
# ============================================================

with left:

    with st.container(border=True):

        st.subheader("▣  Live transcript")

        transcript_placeholder = st.empty()


# ============================================================
# RISK
# ============================================================

with right:

    with st.container(border=True):

        st.subheader("♢  Fraud risk")

        risk_placeholder = st.empty()


st.write("")


# ============================================================
# SIGNALS
# ============================================================

with st.container(border=True):

    st.subheader("⌕  Detected fraud signals")

    signals_placeholder = st.empty()


st.write("")


# ============================================================
# AI ASSESSMENT
# ============================================================

with st.container(border=True):

    st.subheader("☆  AI risk assessment")

    assessment_placeholder = st.empty()


st.write("")


# ============================================================
# TRANSCRIPT RENDERER
# ============================================================

def render_transcript(chunks):

    if not chunks:

        transcript_placeholder.markdown(
            """
            <div class="empty">
                🎙️
                <br><br>
                Start a call to begin real-time monitoring.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    parts = [
        '<div class="transcript-box">'
    ]

    for chunk in chunks:

        speaker = chunk.get(
            "speaker",
            "caller",
        )

        text = html.escape(
            str(
                chunk.get(
                    "text",
                    "",
                )
            )
        )

        if speaker == "caller":

            parts.append(
                '<div class="message">'
                '<span class="caller">'
                '🔴 Caller'
                '</span>'
                '<br>'
                '<span class="message-text">'
                f'{text}'
                '</span>'
                '</div>'
            )

        else:

            parts.append(
                '<div class="message">'
                '<span class="user">'
                '🔵 You'
                '</span>'
                '<br>'
                '<span class="message-text">'
                f'{text}'
                '</span>'
                '</div>'
            )

    parts.append(
        '</div>'
    )

    transcript_placeholder.markdown(
        "".join(parts),
        unsafe_allow_html=True,
    )


# ============================================================
# RISK RENDERER
# ============================================================

def render_risk(risk_data):

    if not risk_data:

        with risk_placeholder.container():

            st.markdown(
                '<div class="risk-number">--%</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="awaiting">'
                'Awaiting call'
                '</div>',
                unsafe_allow_html=True,
            )

            st.progress(0)

            st.caption(
                "🟢 Awaiting call"
            )

        return

    risk = float(
        risk_data.get(
            "risk_score",
            0,
        )
    )

    risk = max(
        0.0,
        min(
            1.0,
            risk,
        ),
    )

    should_warn = bool(
        risk_data.get(
            "should_warn",
            False,
        )
    )

    with risk_placeholder.container():

        st.markdown(
            f'<div class="risk-number">'
            f'{risk * 100:.0f}%'
            f'</div>',
            unsafe_allow_html=True,
        )

        if should_warn:

            st.markdown(
                '<div class="high-risk">'
                '🔴 HIGH RISK'
                '</div>',
                unsafe_allow_html=True,
            )

            st.progress(risk)

            st.caption(
                "High-risk behavior detected"
            )

        else:

            st.markdown(
                '<div class="low-risk">'
                '🟢 LOW RISK'
                '</div>',
                unsafe_allow_html=True,
            )

            st.progress(risk)

            st.caption(
                "No significant fraud indicators"
            )

        st.markdown(
            '<div class="live-status">'
            '● Live AI analysis'
            '</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# SIGNAL RENDERER
# ============================================================

def render_signals(risk_data):

    if not risk_data:

        signals_placeholder.info(
            "🛡️ Start a call to detect fraud signals."
        )

        return

    signals = risk_data.get(
        "signals",
        [],
    )

    detected = [
        signal
        for signal in signals
        if signal.get(
            "present",
            False,
        )
    ]

    if not detected:

        signals_placeholder.info(
            "🛡️ No suspicious signals detected yet."
        )

        return

    readable_names = {

        "urgency":
            "🚨 Urgency",

        "secrecy":
            "🔒 Secrecy / Isolation",

        "authority_impersonation":
            "🏦 Authority Impersonation",

        "credential_request":
            "🔐 Credential Request",

        "coached_script":
            "🗣️ Coached Script",
    }

    with signals_placeholder.container():

        col1, col2 = st.columns(2)

        for index, signal in enumerate(
            detected
        ):

            target = (
                col1
                if index % 2 == 0
                else col2
            )

            name = signal.get(
                "name",
                "Unknown signal",
            )

            evidence = signal.get(
                "evidence",
                "No evidence available.",
            )

            title = readable_names.get(
                name,
                name.replace(
                    "_",
                    " ",
                ).title(),
            )

            title = html.escape(
                str(title)
            )

            evidence = html.escape(
                str(evidence)
            )

            with target:

                st.markdown(
                    '<div class="signal">'
                    '<div class="signal-title">'
                    f'{title}'
                    '</div>'
                    '<div class="signal-text">'
                    '<b>Evidence:</b> '
                    f'{evidence}'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )


# ============================================================
# AI ASSESSMENT RENDERER
# ============================================================

def render_assessment(risk_data):

    if not risk_data:

        with assessment_placeholder.container():

            st.markdown(
                '<span class="ai-badge">'
                'Awaiting call'
                '</span>',
                unsafe_allow_html=True,
            )

            st.write("")

            st.write(
                "An assessment will appear once a call "
                "is being monitored."
            )

        return

    should_warn = bool(
        risk_data.get(
            "should_warn",
            False,
        )
    )

    reasoning = risk_data.get(
        "reasoning",
        "No reasoning was returned.",
    )

    with assessment_placeholder.container():

        if should_warn:

            st.markdown(
                '<span class="ai-badge">'
                'High-risk conversation'
                '</span>',
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                '<span class="ai-badge">'
                'Monitoring conversation'
                '</span>',
                unsafe_allow_html=True,
            )

        st.write("")

        st.write(
            reasoning
        )

        st.caption(
            "Live assessment generated by the AI "
            "fraud detection backend."
        )


# ============================================================
# WARNING RENDERER
# ============================================================

def render_warning(risk_data):

    if not risk_data:

        return

    should_warn = bool(
        risk_data.get(
            "should_warn",
            False,
        )
    )

    if should_warn:

        st.write("")

        st.error(
            "🚨 POSSIBLE FRAUD DETECTED"
        )

        st.markdown(
            "**This conversation contains suspicious behavior.**"
        )

        st.markdown(
            "**Do not share OTPs, PINs, passwords, "
            "or banking details.**"
        )


# ============================================================
# INITIAL DASHBOARD
# ============================================================

render_transcript(
    st.session_state.visible_transcript
)

render_risk(
    st.session_state.risk_data
)

render_signals(
    st.session_state.risk_data
)

render_assessment(
    st.session_state.risk_data
)


# ============================================================
# START CALL
# ============================================================

if start_call:

    try:

        # ----------------------------------------------------
        # Load selected scenario
        # ----------------------------------------------------

        script = load_demo_script(
            call_type
        )

        # ----------------------------------------------------
        # Create unique session
        # ----------------------------------------------------

        session_id = (
            f"call_{int(time.time() * 1000)}"
        )

        st.session_state.call_started = True
        st.session_state.call_running = True
        st.session_state.call_type = call_type
        st.session_state.session_id = session_id
        st.session_state.script = script
        st.session_state.visible_transcript = []
        st.session_state.risk_data = None
        st.session_state.backend_error = None

        # ----------------------------------------------------
        # Connect to backend
        # ----------------------------------------------------

        ws = websocket.create_connection(
            BACKEND_WS_URL,
            timeout=30,
        )

        try:

            # =================================================
            # REAL-TIME CHUNK LOOP
            # =================================================

            for index, chunk in enumerate(
                script
            ):

                # ---------------------------------------------
                # Add chunk to visible transcript
                # ---------------------------------------------

                st.session_state.visible_transcript.append(
                    chunk
                )

                render_transcript(
                    st.session_state.visible_transcript
                )

                # ---------------------------------------------
                # Prepare backend payload
                # ---------------------------------------------

                payload = {
                    "session_id":
                        session_id,

                    "speaker":
                        chunk["speaker"],

                    "timestamp":
                        float(
                            chunk["timestamp"]
                        ),

                    "text":
                        chunk["text"],
                }

                # ---------------------------------------------
                # Send to FastAPI
                # ---------------------------------------------

                ws.send(
                    json.dumps(
                        payload
                    )
                )

                # ---------------------------------------------
                # Receive Groq/AI response
                # ---------------------------------------------

                raw_response = ws.recv()

                risk_data = json.loads(
                    raw_response
                )

                # ---------------------------------------------
                # Save response
                # ---------------------------------------------

                st.session_state.risk_data = (
                    risk_data
                )

                # ---------------------------------------------
                # Update dashboard
                # ---------------------------------------------

                render_risk(
                    risk_data
                )

                render_signals(
                    risk_data
                )

                render_assessment(
                    risk_data
                )

                # ---------------------------------------------
                # Warning appears immediately
                # ---------------------------------------------

                if risk_data.get(
                    "should_warn",
                    False,
                ):

                    render_warning(
                        risk_data
                    )

                # ---------------------------------------------
                # Simulate natural conversation timing
                # ---------------------------------------------

                if index < len(script) - 1:

                    time.sleep(
                        CHUNK_DELAY
                    )

        finally:

            ws.close()

        # ----------------------------------------------------
        # Call completed
        # ----------------------------------------------------

        st.session_state.call_running = False

        st.session_state.call_started = True

        # ----------------------------------------------------
        # Final dashboard refresh
        # ----------------------------------------------------

        st.rerun()

    except FileNotFoundError:

        st.session_state.call_started = False
        st.session_state.call_running = False
        st.session_state.script = []
        st.session_state.visible_transcript = []
        st.session_state.risk_data = None

        st.error(
            f"Demo file not found in: {DEMO_DIR}"
        )

        st.code(
            "Demo/scam_call_script.json\n"
            "Demo/normal_call_script.json"
        )

    except websocket.WebSocketException as e:

        st.session_state.call_running = False
        st.session_state.backend_error = str(e)

        st.error(
            "🚨 Could not connect to the FastAPI backend."
        )

        st.code(
            f"Backend: {BACKEND_WS_URL}\n\n"
            f"Error: {e}"
        )

    except Exception as e:

        st.session_state.call_running = False
        st.session_state.backend_error = str(e)

        st.error(
            "🚨 An error occurred during the call simulation."
        )

        st.code(
            str(e)
        )


# ============================================================
# FINAL WARNING
# ============================================================

if (
    st.session_state.call_started
    and not st.session_state.call_running
    and st.session_state.risk_data
    and not start_call
):

    render_warning(
        st.session_state.risk_data
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    '🛡️ Fraud Guardian'
    '&nbsp;•&nbsp;'
    'Protecting you from fraud, in real time.'
    '</div>',
    unsafe_allow_html=True,
)