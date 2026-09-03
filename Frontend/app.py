import json
import html
import time
import base64
from pathlib import Path

import streamlit as st
import websocket


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DEMO_DIR = BASE_DIR / "Demo"

NORMAL_SCRIPT = DEMO_DIR / "normal_call_script.json"
SCAM_SCRIPT = DEMO_DIR / "scam_call_script.json"

ALARM_PATH = DEMO_DIR / "alarm_sound_mp3"


# ============================================================
# BACKEND
# ============================================================

BACKEND_WS_URL = "ws://127.0.0.1:8000/ws/assess-call"

CHUNK_DELAY = 1.5


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
# SESSION STATE
# ============================================================

defaults = {
    "call_running": False,
    "call_started": False,
    "scenario": "Scam Call",
    "session_id": "",
    "transcript": [],
    "risk_score": 0.0,
    "signals": [],
    "reasoning": "Waiting for call analysis...",
    "should_warn": False,
    "alarm_played": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

html, body, [class*="css"] {
    font-family: Arial, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(48, 103, 82, 0.35), transparent 35%),
        linear-gradient(135deg, #071d16 0%, #0d3025 50%, #123d30 100%);
    color: #f5faf7;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: #061710;
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: #e9f5ef !important;
}

.sidebar-title {
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 4px;
}

.sidebar-subtitle {
    font-size: 14px;
    color: #a9c2b7;
    margin-bottom: 30px;
}

.sidebar-status {
    background: rgba(55, 190, 128, 0.12);
    border: 1px solid rgba(55, 190, 128, 0.25);
    padding: 14px;
    border-radius: 14px;
    margin-top: 20px;
}

.sidebar-status-title {
    font-weight: 700;
    font-size: 15px;
}

.sidebar-status-text {
    font-size: 13px;
    color: #a9c2b7;
    margin-top: 4px;
}


/* Main header */

.main-title {
    font-size: 42px;
    font-weight: 850;
    letter-spacing: -1px;
    margin-bottom: 4px;
}

.main-subtitle {
    color: #b6cec3;
    font-size: 17px;
    margin-bottom: 24px;
}

.system-active {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(55, 190, 128, 0.12);
    border: 1px solid rgba(55, 190, 128, 0.28);
    color: #9df0c4;
    padding: 8px 14px;
    border-radius: 30px;
    font-size: 14px;
    font-weight: 700;
}

.active-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #54d890;
    display: inline-block;
}


/* Cards */

.card {
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 18px;
    backdrop-filter: blur(8px);
}

.card-title {
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 16px;
}

.card-subtitle {
    color: #9fb8ad;
    font-size: 13px;
    margin-top: -10px;
    margin-bottom: 15px;
}


/* Transcript */

.transcript-box {
    background: rgba(0,0,0,0.16);
    border-radius: 16px;
    padding: 16px;
    min-height: 360px;
    max-height: 470px;
    overflow-y: auto;
}

.message-row {
    display: flex;
    margin-bottom: 13px;
    width: 100%;
}

.message-row.caller {
    justify-content: flex-start;
}

.message-row.user {
    justify-content: flex-end;
}

.message-bubble {
    max-width: 82%;
    padding: 13px 16px;
    border-radius: 17px;
    line-height: 1.5;
    font-size: 16px;
}

.caller-bubble {
    background: #173d30;
    border-bottom-left-radius: 5px;
}

.user-bubble {
    background: #28644d;
    border-bottom-right-radius: 5px;
}

.speaker-label {
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    opacity: 0.72;
    margin-bottom: 4px;
}

.message-text {
    font-size: 16px;
}


/* Risk */

.risk-number {
    font-size: 54px;
    font-weight: 900;
    line-height: 1;
    margin-top: 8px;
}

.risk-label {
    font-size: 16px;
    font-weight: 800;
    margin-top: 8px;
}

.risk-bar {
    height: 16px;
    background: rgba(255,255,255,0.10);
    border-radius: 20px;
    overflow: hidden;
    margin-top: 20px;
}

.risk-fill {
    height: 100%;
    border-radius: 20px;
}

.risk-low {
    background: #46c986;
}

.risk-medium {
    background: #e5bd55;
}

.risk-high {
    background: #ef6c67;
}


/* Signals */

.signal {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 13px;
    padding: 13px 14px;
    margin-bottom: 10px;
}

.signal-name {
    font-weight: 800;
    font-size: 14px;
}

.signal-evidence {
    color: #aec5bb;
    font-size: 13px;
    margin-top: 4px;
}

.signal-icon {
    font-size: 17px;
    margin-right: 7px;
}


/* Assessment */

.reasoning-box {
    background: rgba(255,255,255,0.045);
    border-left: 4px solid #63c99a;
    border-radius: 10px;
    padding: 15px 17px;
    color: #d8e9e1;
    line-height: 1.55;
}


/* Warning */

.warning-box {
    background: linear-gradient(
        135deg,
        rgba(150, 32, 32, 0.95),
        rgba(100, 18, 18, 0.97)
    );
    border: 2px solid rgba(255, 110, 110, 0.75);
    border-radius: 22px;
    padding: 28px;
    margin: 20px 0;
    text-align: center;
    box-shadow: 0 0 35px rgba(255, 60, 60, 0.22);
}

.warning-title {
    font-size: 30px;
    font-weight: 900;
    margin-bottom: 10px;
}

.warning-text {
    font-size: 17px;
    line-height: 1.55;
    color: #ffe7e7;
}


/* Call controls */

.control-card {
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
}

.footer {
    text-align: center;
    color: #75998b;
    font-size: 12px;
    margin-top: 35px;
    padding-bottom: 20px;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def load_script(scenario):
    if scenario == "Scam Call":
        script_path = SCAM_SCRIPT
    else:
        script_path = NORMAL_SCRIPT

    if not script_path.exists():
        st.error(f"Demo script not found: {script_path}")
        return []

    try:
        with open(script_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        st.error(f"Could not load demo script: {exc}")
        return []


def find_alarm_file():
    """
    Finds an alarm audio file inside Demo/alarm_sound_mp3.

    Supports:
    - alarm_sound_mp3 as a file
    - alarm_sound_mp3 as a directory
    - mp3, wav, ogg, m4a files
    """

    if ALARM_PATH.is_file():
        return ALARM_PATH

    if ALARM_PATH.is_dir():
        supported = {".mp3", ".wav", ".ogg", ".m4a"}

        for file in ALARM_PATH.rglob("*"):
            if file.is_file() and file.suffix.lower() in supported:
                return file

    # Fallback: search Demo directory
    if DEMO_DIR.exists():
        supported = {".mp3", ".wav", ".ogg", ".m4a"}

        for file in DEMO_DIR.rglob("*"):
            if file.is_file() and file.suffix.lower() in supported:
                return file

    return None


def get_audio_mime(audio_path):
    suffix = audio_path.suffix.lower()

    if suffix == ".mp3":
        return "audio/mpeg"

    if suffix == ".wav":
        return "audio/wav"

    if suffix == ".ogg":
        return "audio/ogg"

    if suffix == ".m4a":
        return "audio/mp4"

    return "audio/mpeg"


def play_alarm():
    """
    Injects an autoplaying audio element.

    The Start Call button is a user interaction, so modern browsers
    are more likely to allow autoplay during the demo.
    """

    alarm_file = find_alarm_file()

    if alarm_file is None:
        st.warning(
            "⚠️ Alarm file not found. Put an MP3/WAV/OGG file inside "
            "Demo/alarm_sound_mp3."
        )
        return

    try:
        audio_bytes = alarm_file.read_bytes()
        encoded = base64.b64encode(audio_bytes).decode("utf-8")
        mime = get_audio_mime(alarm_file)

        audio_html = (
            f'<audio autoplay>'
            f'<source src="data:{mime};base64,{encoded}" type="{mime}">'
            f'</audio>'
        )

        st.markdown(audio_html, unsafe_allow_html=True)

    except Exception as exc:
        st.warning(f"Could not play alarm sound: {exc}")


def risk_level(score):
    if score >= 0.70:
        return "HIGH RISK", "risk-high"

    if score >= 0.40:
        return "MEDIUM RISK", "risk-medium"

    return "LOW RISK", "risk-low"


# ============================================================
# UI RENDER FUNCTIONS
# ============================================================

def render_header():
    st.markdown(
        '<div class="main-title">🛡️ Fraud Guardian</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">'
        "Real-Time In-Call Fraud Detection"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="system-active">'
        '<span class="active-dot"></span>'
        "Detection System Active"
        "</div>",
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-title">🛡️ Fraud Guardian</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-subtitle">'
            "Protecting vulnerable callers from fraud and manipulation."
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown("### Navigation")

        st.markdown("📞 **Live Call**")
        st.markdown("📊 Risk Analysis")
        st.markdown("🧠 AI Assessment")
        st.markdown("📝 Call History")

        st.markdown(
            '<div class="sidebar-status">'
            '<div class="sidebar-status-title">● System Online</div>'
            '<div class="sidebar-status-text">'
            "AI fraud monitoring is ready."
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )


def render_call_controls():
    st.markdown(
        '<div class="control-card">'
        '<div class="card-title">📞 Call Simulation</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        scenario = st.selectbox(
            "Scenario",
            ["Scam Call", "Normal Call"],
            index=0 if st.session_state.scenario == "Scam Call" else 1,
            disabled=st.session_state.call_running,
        )

        st.session_state.scenario = scenario

    with col2:
        start_clicked = st.button(
            "▶ Start Call",
            use_container_width=True,
            disabled=st.session_state.call_running,
        )

    with col3:
        stop_clicked = st.button(
            "■ Stop Call",
            use_container_width=True,
            disabled=not st.session_state.call_running,
        )

    return start_clicked, stop_clicked


def render_transcript(container):
    parts = []

    for item in st.session_state.transcript:
        speaker = item["speaker"]
        text = html.escape(str(item["text"]))

        if speaker == "caller":
            parts.append(
                '<div class="message-row caller">'
                '<div class="message-bubble caller-bubble">'
                '<div class="speaker-label">Caller</div>'
                f'<div class="message-text">{text}</div>'
                "</div>"
                "</div>"
            )
        else:
            parts.append(
                '<div class="message-row user">'
                '<div class="message-bubble user-bubble">'
                '<div class="speaker-label">You</div>'
                f'<div class="message-text">{text}</div>'
                "</div>"
                "</div>"
            )

    if not parts:
        parts.append(
            '<div style="text-align:center; padding:120px 20px; '
            'color:#78998c;">'
            "Waiting for the call to begin..."
            "</div>"
        )

    transcript_html = (
        '<div class="card">'
        '<div class="card-title">💬 Live Transcript</div>'
        '<div class="card-subtitle">'
        "Conversation is analyzed in real time."
        "</div>"
        '<div class="transcript-box">'
        + "".join(parts)
        + "</div>"
        "</div>"
    )

    container.markdown(
        transcript_html,
        unsafe_allow_html=True,
    )


def render_risk(container):
    score = max(0.0, min(1.0, float(st.session_state.risk_score)))
    percentage = int(round(score * 100))

    label, css_class = risk_level(score)

    width = f"{percentage}%"

    risk_html = (
        '<div class="card">'
        '<div class="card-title">🚨 Fraud Risk</div>'
        '<div class="risk-number">'
        f"{percentage}%"
        "</div>"
        f'<div class="risk-label">{label}</div>'
        '<div class="risk-bar">'
        f'<div class="risk-fill {css_class}" style="width:{width};"></div>'
        "</div>"
        "</div>"
    )

    container.markdown(
        risk_html,
        unsafe_allow_html=True,
    )


def render_signals(container):
    present_signals = [
        signal
        for signal in st.session_state.signals
        if signal.get("present", False)
    ]

    parts = [
        '<div class="card">',
        '<div class="card-title">🔎 Detected Signals</div>',
    ]

    if not present_signals:
        parts.append(
            '<div style="color:#9fb8ad; padding:10px 0;">'
            "No significant fraud signals detected yet."
            "</div>"
        )

    else:
        for signal in present_signals:
            name = html.escape(
                str(signal.get("name", "Unknown")).replace("_", " ").title()
            )

            evidence = html.escape(
                str(signal.get("evidence", ""))
            )

            parts.append(
                '<div class="signal">'
                f'<div class="signal-name">'
                f'<span class="signal-icon">⚠️</span>{name}'
                "</div>"
                f'<div class="signal-evidence">{evidence}</div>'
                "</div>"
            )

    parts.append("</div>")

    container.markdown(
        "".join(parts),
        unsafe_allow_html=True,
    )


def render_assessment(container):
    reasoning = html.escape(
        str(st.session_state.reasoning)
    )

    assessment_html = (
        '<div class="card">'
        '<div class="card-title">🧠 AI Risk Assessment</div>'
        '<div class="reasoning-box">'
        f"{reasoning}"
        "</div>"
        "</div>"
    )

    container.markdown(
        assessment_html,
        unsafe_allow_html=True,
    )


def render_warning(container):
    if not st.session_state.should_warn:
        container.empty()
        return

    warning_html = (
        '<div class="warning-box">'
        '<div class="warning-title">🚨 FRAUD WARNING</div>'
        '<div class="warning-text">'
        "<strong>This call shows multiple signs of fraud.</strong><br><br>"
        "Do not share OTPs, PINs, passwords, or banking information. "
        "Do not follow instructions to hide the call from your family "
        "or bank staff.<br><br>"
        "<strong>Stop the call and verify independently.</strong>"
        "</div>"
        "</div>"
    )

    container.markdown(
        warning_html,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR + HEADER
# ============================================================

render_sidebar()

render_header()

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# CALL CONTROLS
# ============================================================

start_clicked, stop_clicked = render_call_controls()


# ============================================================
# MAIN DASHBOARD PLACEHOLDERS
# ============================================================

left_col, right_col = st.columns([1.55, 1])

with left_col:
    transcript_placeholder = st.empty()

with right_col:
    risk_placeholder = st.empty()
    signals_placeholder = st.empty()
    assessment_placeholder = st.empty()

warning_placeholder = st.empty()


# ============================================================
# INITIAL DASHBOARD
# ============================================================

render_transcript(transcript_placeholder)
render_risk(risk_placeholder)
render_signals(signals_placeholder)
render_assessment(assessment_placeholder)
render_warning(warning_placeholder)


# ============================================================
# STOP CALL
# ============================================================

if stop_clicked:
    st.session_state.call_running = False
    st.session_state.call_started = False
    st.session_state.should_warn = False
    st.session_state.alarm_played = False

    st.rerun()


# ============================================================
# START CALL
# ============================================================

if start_clicked:

    script = load_script(st.session_state.scenario)

    if not script:
        st.stop()

    # Reset call state
    st.session_state.call_running = True
    st.session_state.call_started = True
    st.session_state.session_id = (
        f"demo_{int(time.time())}"
    )

    st.session_state.transcript = []
    st.session_state.risk_score = 0.0
    st.session_state.signals = []
    st.session_state.reasoning = (
        "AI analysis will appear as the conversation progresses."
    )
    st.session_state.should_warn = False
    st.session_state.alarm_played = False

    # Update dashboard
    render_transcript(transcript_placeholder)
    render_risk(risk_placeholder)
    render_signals(signals_placeholder)
    render_assessment(assessment_placeholder)
    render_warning(warning_placeholder)

    ws = None

    try:

        # ----------------------------------------------------
        # ONE WEBSOCKET CONNECTION FOR THE WHOLE CALL
        # ----------------------------------------------------

        ws = websocket.create_connection(
            BACKEND_WS_URL,
            timeout=30,
        )

        for chunk in script:

            # -----------------------------------------------
            # ADD MESSAGE TO VISIBLE TRANSCRIPT
            # -----------------------------------------------

            st.session_state.transcript.append(
                {
                    "speaker": chunk["speaker"],
                    "text": chunk["text"],
                }
            )

            render_transcript(transcript_placeholder)

            # -----------------------------------------------
            # SEND CHUNK TO BACKEND
            # -----------------------------------------------

            payload = {
                "session_id": st.session_state.session_id,
                "speaker": chunk["speaker"],
                "text": chunk["text"],
                "timestamp": chunk.get(
                    "timestamp",
                    time.time(),
                ),
            }

            ws.send(json.dumps(payload))

            # -----------------------------------------------
            # RECEIVE AI RESPONSE
            # -----------------------------------------------

            response_text = ws.recv()

            response = json.loads(response_text)

            # -----------------------------------------------
            # UPDATE RISK
            # -----------------------------------------------

            st.session_state.risk_score = float(
                response.get("risk_score", 0.0)
            )

            st.session_state.signals = response.get(
                "signals",
                [],
            )

            st.session_state.reasoning = response.get(
                "reasoning",
                "No reasoning returned.",
            )

            st.session_state.should_warn = bool(
                response.get("should_warn", False)
            )

            # -----------------------------------------------
            # UPDATE UI
            # -----------------------------------------------

            render_risk(risk_placeholder)
            render_signals(signals_placeholder)
            render_assessment(assessment_placeholder)
            render_warning(warning_placeholder)

            # -----------------------------------------------
            # ALARM
            # -----------------------------------------------

            if (
                st.session_state.should_warn
                and not st.session_state.alarm_played
            ):
                st.session_state.alarm_played = True

                # Display the alarm player.
                # It is triggered immediately after the user
                # has interacted with Start Call.
                play_alarm()

            # -----------------------------------------------
            # WAIT BEFORE NEXT TRANSCRIPT CHUNK
            # -----------------------------------------------

            time.sleep(CHUNK_DELAY)

        # ----------------------------------------------------
        # CALL FINISHED
        # ----------------------------------------------------

        if ws:
            ws.close()

        st.session_state.call_running = False

        st.success(
            f"{st.session_state.scenario} simulation completed."
        )

        time.sleep(0.5)

        st.rerun()

    except websocket.WebSocketException as exc:

        st.session_state.call_running = False

        st.error(
            "Could not connect to the Fraud Guardian backend.\n\n"
            f"Backend URL: {BACKEND_WS_URL}\n\n"
            f"Details: {exc}"
        )

    except Exception as exc:

        st.session_state.call_running = False

        st.error(
            f"An error occurred during the call simulation: {exc}"
        )

    finally:

        if ws is not None:
            try:
                ws.close()
            except Exception:
                pass


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    "Fraud Guardian • Real-Time AI In-Call Fraud Detection"
    "</div>",
    unsafe_allow_html=True,
)