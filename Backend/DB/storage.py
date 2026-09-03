import sqlite3
import json
from Backend.Models.schemas import TranscriptChunk, RiskScoreResponse

DB_FILE = "fraud_detection.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS call_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                speaker TEXT,
                text TEXT,
                timestamp REAL,
                risk_score REAL,
                should_warn INTEGER,
                reasoning TEXT,
                signals TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def log_event(chunk: TranscriptChunk, score_res: RiskScoreResponse):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            signals_json = json.dumps([s.model_dump() for s in score_res.signals])
            cursor.execute("""
                INSERT INTO call_logs 
                (session_id, speaker, text, timestamp, risk_score, should_warn, reasoning, signals)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chunk.session_id,
                chunk.speaker,
                chunk.text,
                chunk.timestamp,
                score_res.risk_score,
                1 if score_res.should_warn else 0,
                score_res.reasoning,
                signals_json
            ))
            conn.commit()
    except Exception as e:
        print(f"[DB Error] Failed to log chunk: {e}")