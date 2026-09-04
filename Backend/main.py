import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from Backend.Models.schemas import TranscriptChunk, RiskScoreResponse, RiskSignal
from Backend.Core.risk_engine import process_chunk
from Backend.DB.storage import init_db, log_event

# Set to False to use your teammate's live Groq LLM model
STUB_MODE = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="In-Call Fraud Detection API", lifespan=lifespan)

def stub_score_chunk(chunk: TranscriptChunk) -> RiskScoreResponse:
    """Fallback stub for testing network flow without burning API credits."""
    mock_signals = [
        RiskSignal(name="urgency", present=False, evidence="none"),
        RiskSignal(name="secrecy", present=False, evidence="none"),
        RiskSignal(name="authority_impersonation", present=False, evidence="none"),
        RiskSignal(name="credential_request", present=False, evidence="none"),
        RiskSignal(name="coached_script", present=False, evidence="none")
    ]
    return RiskScoreResponse(
        session_id=chunk.session_id,
        risk_score=0.1,
        signals=mock_signals,
        reasoning="Stub mode active.",
        should_warn=False
    )

@app.websocket("/ws/assess-call")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 1. Receive JSON payload from client
            data = await websocket.receive_text()
            chunk_dict = json.loads(data)
            chunk = TranscriptChunk(**chunk_dict)

            # 2. Process chunk through risk engine (updates buffer + calls LLM)
            if STUB_MODE:
                score_response = stub_score_chunk(chunk)
            else:
                score_response = process_chunk(chunk)

            # 3. Log event to SQLite database
            if score_response.should_warn:
                log_event(chunk, score_response)

            # 4. Return serialized evaluation to frontend
            await websocket.send_text(score_response.model_dump_json())

    except WebSocketDisconnect:
        print("Client disconnected from WebSocket.")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        await websocket.close()