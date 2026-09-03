import os
import json
from groq import Groq
from dotenv import load_dotenv
from Backend.Models.schemas import RiskScoreResponse, RiskSignal

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """You are a real-time fraud-coaching detector analyzing a live phone call transcript involving a bank customer.

Score the conversation so far for signs the customer is being coached or manipulated by a scammer, specifically:
- urgency: pressure to act immediately, no time to think
- secrecy: instructions to not tell anyone (family, bank staff, police)
- authority_impersonation: caller claims to be bank/police/government official
- credential_request: asking for OTP, PIN, password, or remote screen access
- coached_script: caller is telling the customer exactly what to say or do at the bank

A single signal alone is often NOT a scam (e.g. a legitimate urgent request). Score based on the COMBINATION and buildup of signals across turns, not any one phrase in isolation.

Respond with ONLY valid JSON, no other text, in this exact shape:
{
  "risk_score": <float 0.0-1.0>,
  "signals": [
    {"name": "urgency", "present": <bool>, "evidence": "<short quote or 'none'>"},
    {"name": "secrecy", "present": <bool>, "evidence": "<short quote or 'none'>"},
    {"name": "authority_impersonation", "present": <bool>, "evidence": "<short quote or 'none'>"},
    {"name": "credential_request", "present": <bool>, "evidence": "<short quote or 'none'>"},
    {"name": "coached_script", "present": <bool>, "evidence": "<short quote or 'none'>"}
  ],
  "reasoning": "<one sentence explaining the score>"
}
"""


def score_chunk(session_id: str, rolling_transcript: str) -> RiskScoreResponse:
    completion = client.chat.completions.create(
        model=MODEL,
        max_completion_tokens=800,       # more headroom
        temperature=0.2,
        reasoning_effort="low",           # don't burn tokens on internal reasoning
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Transcript so far:\n\n{rolling_transcript}"},
        ],
    )

    raw_text = completion.choices[0].message.content.strip()

    # Robust extraction: grab only the {...} block, ignore any stray text around it
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model output: {raw_text!r}")
    json_str = raw_text[start:end + 1]

    parsed = json.loads(json_str)

    signals = [RiskSignal(**s) for s in parsed["signals"]]
    signal_count = sum(1 for s in signals if s.present)

    should_warn = parsed["risk_score"] >= 0.6 and signal_count >= 2

    return RiskScoreResponse(
        session_id=session_id,
        risk_score=parsed["risk_score"],
        signals=signals,
        reasoning=parsed["reasoning"],
        should_warn=should_warn,
    )