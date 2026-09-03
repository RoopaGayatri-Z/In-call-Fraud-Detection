# In-call-Fraud-Detection (Fraud Guardian)

**Real-time LLM-powered detection of social-engineering fraud during live calls.**

Fraud Guardian is a prototype system that protects vulnerable customers—especially senior citizens and first-time digital banking users—from live scam calls. Instead of blocking numbers before a call or analyzing patterns after it ends, Fraud Guardian scores the conversation **as it happens**, and warns the user in plain language the moment risk becomes high.

---

## Problem Statement

**Protecting Vulnerable Customers from Digital Financial Fraud**  
Focus: social engineering during live scam calls targeting:

- Senior citizens  
- First-time digital banking users  

Existing defenses are mostly:

- **Pre-call:** blocklists, caller ID, spam labels  
- **Post-call:** transaction monitoring, retrospective pattern analysis  

Both miss the critical window: **during the call**, when the victim is being actively coached to transfer money, share OTPs, or reveal credentials.

Fraud Guardian adds the missing **“during” layer**: a real-time in-call LLM detection engine that watches the transcript stream, maintains conversational context, and triggers an immediate, elderly-friendly warning when risk crosses a threshold.

---

## Why This Matters

- Real-time coaching scams (“stay on the line”, “don’t tell anyone”, “tell the bank it’s for family emergency”) are rising.  
- Elderly and new digital users are disproportionately targeted and less likely to recognize subtle manipulation.  
- Recent research (e.g., CHI 2025, *“It Warned Me Just at the Right Moment”*) shows that **real-time in-call LLM detection** is validated but still underexplored in practice.  

This project is built specifically for this “during-call” moment, with UX designed for non-technical users.

---

## How It Works (High Level)

1. A call transcript (live or simulated) is sent to the backend in **rolling chunks**.  
2. The backend maintains a **per-session rolling transcript** and conversational context.  
3. An **LLM scorer (Groq)**:
   - Builds a prompt from the current transcript window  
   - Calls the LLM via Groq  
   - Parses a structured **risk JSON** (e.g., score + reasons)  
4. A **risk engine**:
   - Applies rolling-window + threshold logic  
   - Decides when risk is high enough to trigger a warning  
5. When the threshold is crossed:
   - The frontend shows a **clear visual warning**  
   - A **spoken warning** can be played (elderly-friendly, plain language)  
   - The user gets a moment to **pause before any transfer or credential sharing**  

The system focuses on **behavioral signals** such as:

- Urgency and pressure (“do this now”, “you’ll lose money if you wait”)  
- Secrecy / isolation (“don’t tell anyone”, “keep this call private”)  
- Coaching language (“tell the bank officer that…”)  
- Requests for OTPs, passwords, or other credentials  

---

## Repo Structure

```text
In-call-Fraud-Detection/
├── README.md
├── requirements.txt
├── .env.example
├── backend/
│   ├── main.py                  # FastAPI app + WebSocket endpoint
│   ├── core/
│   │   ├── llm_scorer.py        # builds prompt, calls LLM, parses risk JSON
│   │   ├── risk_engine.py       # rolling window + threshold logic
│   │   └── transcript_buffer.py # per-session rolling transcript state
│   ├── models/
│   │   └── schemas.py           # pydantic request/response models
│   └── db/
│       └── storage.py           # SQLite session logging
├── frontend/
│   └── app.py                   # Streamlit: call simulator, live risk meter, warning overlay
├── demo/
│   ├── scam_call_script.json    # scripted scam transcript, chunked
│   ├── normal_call_script.json  # scripted safe-call transcript (shows no false alarm)
└── tests/
    └── test_risk_engine.py
```

---

## Features

- **Real-time risk scoring** of call transcripts using an LLM (Groq)  
- **Rolling-window context** to capture buildup of manipulation, not just isolated phrases  
- **Threshold-based warnings** tuned to reduce false alarms while catching high-risk patterns  
- **Elderly-friendly UX**:
  - Simple, large-text warnings  
  - Plain-language explanations (“This call looks like a scam. Do not share OTPs or transfer money.”)  
  - Optional spoken alert  
- **Demo mode**:
  - Simulated scam call script that triggers warnings  
  - Normal call script that should **not** trigger false alarms  

### Application Interface

![Fraud Guardian Dashboard Screenshot]("C:\Users\Roopa\Downloads\fraud_detection.jpeg")
*(Example view of the Streamlit dashboard capturing an ongoing scam attempt with high-risk signals).*

---

## Tech Stack

- **Backend:**  
  - Python  
  - FastAPI  
  - WebSockets for streaming transcript chunks  
  - SQLite for session logging  

- **Frontend:**  
  - Streamlit  
  - Live risk meter + warning overlay + call simulator  

- **AI / ML:**  
  - LLM-based risk scorer via **Groq**  
  - Rule + threshold-based risk engine on top of LLM outputs  

- **Testing:**  
  - `pytest` for risk engine logic  

---

## Installation

### Prerequisites

- Python 3.10+  
- `pip`  
- A Groq API key (sign up at https://console.groq.com)

### Clone the Repo

```bash
git clone https://github.com/RoopaGayatri-Z/In-call-Fraud-Detection.git
cd In-call-Fraud-Detection
```

### Set Up Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure Environment Variables

Copy the example env file:

```bash
cp .env.example .env
```

Edit `.env` and set at least:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Adjust `GROQ_MODEL` to whatever model you are using.

---

## Running the System

### Start the Backend (FastAPI)

From the project root:

```bash
uvicorn backend.main:app --reload
```

The API will typically be available at:  
`http://127.0.0.1:8000`

Check interactive docs at:  
`http://127.0.0.1:8000/docs`

### Start the Frontend (Streamlit)

In another terminal (with the same venv activated):

```bash
streamlit run frontend/app.py
```

Open the URL shown by Streamlit (usually `http://localhost:8501`).

---

## Using the Demo

In the Streamlit app:

1. Choose a demo script:
   - **Scam call** – should show rising risk and trigger a warning  
   - **Normal call** – should stay low risk, demonstrating low false alarms  
2. Start the simulation.  
3. Watch:
   - The **live risk meter**  
   - The **transcript chunks** being processed  
   - The **warning overlay** when risk crosses the threshold  

This is intended as a **proof-of-concept demo** for the “during-call” detection idea.

---

## API Overview (Backend)

Key endpoints (exact paths may vary slightly depending on your code):

- `POST /session` – create a new call session  
- `WS /ws/session/{session_id}` – WebSocket to stream transcript chunks and receive risk updates  
- `GET /session/{session_id}` – retrieve session metadata and risk history (for debugging / logs)  

Request/response shapes are defined in `backend/models/schemas.py` using Pydantic.

---

## Testing

Run tests with:

```bash
pytest tests/
```

Currently includes:

- `test_risk_engine.py` – unit tests for rolling-window and threshold logic  

You can extend this with:

- LLM scorer integration tests (with mocked LLM responses)  
- End-to-end tests that simulate full demo calls  

---

## Design Choices & Notes

- **Rolling transcript buffer**: Keeps recent context while limiting token usage and latency.  
- **LLM scoring + rule engine**:  
  - LLM captures nuanced social-engineering patterns  
  - Rule/threshold layer stabilizes decisions and reduces jitter  
- **Elderly-focused UX**:  
  - Warnings are explicit, calm, and actionable  
  - Avoids technical jargon (“risk score”, “model confidence”) in user-facing messages  

---

## Limitations & Future Work

**Current limitations:**

- Demo uses **simulated transcripts**, not real telephony integration.  
- LLM provider (Groq) is external; latency and cost depend on that provider.  
- Thresholds and prompts are hand-tuned on limited scripts; broader evaluation is needed.  

**Possible next steps:**

- Integrate with real VoIP / telephony stack (e.g., Twilio, Asterisk).  
- Collect and evaluate on a larger, diverse set of real/partially-real call transcripts.  
- Add multilingual support and localization for different regions.  
- Explore on-device or privacy-preserving LLM options for sensitive data.  
- Conduct user studies with elderly participants to refine warning wording and timing.  

---

## Team

- Vuchuru Siri  
- Danda Nanditha  
- Pabolu Roopa Gayatri  

---

## License

All rights reserved. This repository is a proof-of-concept prototype and is currently not licensed for public distribution, modification, or commercial use.


---

## Contact

For questions, collaboration, or feedback:

- GitHub: https://github.com/RoopaGayatri-Z/In-call-Fraud-Detection  
