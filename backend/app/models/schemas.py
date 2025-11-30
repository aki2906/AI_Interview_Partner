from pydantic import BaseModel
from typing import List, Optional, Any

class InterviewStartRequest(BaseModel):
    domain: str
    difficulty: str

class InterviewStartResponse(BaseModel):
    session_id: str
    message: str
    first_question: str

# NEW: Model for Text Input
class TextSubmitRequest(BaseModel):
    session_id: str
    text: str

class EvaluationResponse(BaseModel):
    transcription: str
    score: int
    feedback: str
    improvements: str
    next_question: Optional[str] = None
    is_interview_over: bool = False

class ReportResponse(BaseModel):
    total_score: float
    summary: str
    domain: str
    history: List[Any]
