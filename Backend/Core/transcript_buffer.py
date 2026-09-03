class TranscriptBuffer:
    """Keeps a rolling per-session transcript so scoring has conversational context."""

    def __init__(self, max_turns: int = 12):
        self.max_turns = max_turns
        self._sessions: dict[str, list[str]] = {}

    def add_turn(self, session_id: str, speaker: str, text: str) -> str:
        self._sessions.setdefault(session_id, [])
        self._sessions[session_id].append(f"{speaker}: {text}")
        # keep only the most recent N turns so context doesn't grow unbounded
        self._sessions[session_id] = self._sessions[session_id][-self.max_turns:]
        return self.get_transcript(session_id)

    def get_transcript(self, session_id: str) -> str:
        return "\n".join(self._sessions.get(session_id, []))

    def reset(self, session_id: str):
        self._sessions.pop(session_id, None)