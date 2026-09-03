import json
import time
from Backend.Core.risk_engine import process_chunk
from Backend.Models.schemas import TranscriptChunk


def run_script(path: str, session_id: str):
    with open(path) as f:
        turns = json.load(f)

    print(f"\n=== Running {path} ===")
    for turn in turns:
        chunk = TranscriptChunk(
            session_id=session_id,
            speaker=turn["speaker"],
            text=turn["text"],
            timestamp=turn["timestamp"],
        )
        result = process_chunk(chunk)
        print(f"[{turn['speaker']}] {turn['text']}")
        print(f"  -> risk_score={result.risk_score:.2f} should_warn={result.should_warn}")
        print(f"  -> reasoning: {result.reasoning}")
        if result.should_warn:
            print("  !! WARNING TRIGGERED !!")
            break


if __name__ == "__main__":
    run_script("demo/scam_call_script.json", "session-scam-1")
    run_script("demo/normal_call_script.json", "session-normal-1")