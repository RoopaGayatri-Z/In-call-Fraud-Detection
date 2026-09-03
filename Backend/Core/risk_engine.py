from Backend.Core.transcript_buffer import TranscriptBuffer
from Backend.Core.llm_scorer import score_chunk
from Backend.Models.schemas import TranscriptChunk, RiskScoreResponse

buffer = TranscriptBuffer()


def process_chunk(chunk: TranscriptChunk) -> RiskScoreResponse:
    rolling_transcript = buffer.add_turn(chunk.session_id, chunk.speaker, chunk.text)
    result = score_chunk(chunk.session_id, rolling_transcript)
    return result