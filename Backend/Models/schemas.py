# backend/models/schemas.py
from pydantic import BaseModel
from typing import Literal

class TranscriptChunk(BaseModel):
    session_id: str
    speaker: Literal["caller", "user"]
    text: str
    timestamp: float

class RiskSignal(BaseModel):
    name: str          # e.g. "urgency", "secrecy", "authority_impersonation", "credential_request", "coached_script"
    present: bool
    evidence: str       # short quote/reasoning from transcript

class RiskScoreResponse(BaseModel):
    session_id: str
    risk_score: float   # 0-1
    signals: list[RiskSignal]
    reasoning: str
    should_warn: bool