from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
import traceback
from app.models.schemas import InterviewStartRequest, InterviewStartResponse, EvaluationResponse, ReportResponse, TextSubmitRequest
from app.services.audio_service import transcribe_audio
from app.services.ai_service import generate_question, evaluate_answer, generate_final_report
from app.config import settings

app = FastAPI(title="AI Interview Partner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS = {}

@app.post("/start", response_model=InterviewStartResponse)
async def start_interview(request: InterviewStartRequest):
    try:
        session_id = str(uuid4())
        print(f"Starting session: {session_id}")
        
        first_q = await generate_question(request.domain, request.difficulty, [], 1)
        
        SESSIONS[session_id] = {
            "domain": request.domain,
            "difficulty": request.difficulty,
            "history": [],
            "full_log": [{"role": "assistant", "content": first_q}],
            "current_q": first_q,
            "scores": [],
            "q_count": 1
        }
        
        return InterviewStartResponse(
            session_id=session_id,
            message="Started",
            first_question=first_q
        )
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# --- AUDIO SUBMISSION ---
@app.post("/submit-audio", response_model=EvaluationResponse)
async def submit_audio(session_id: str = Form(...), file: UploadFile = File(...)):
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_bytes = await file.read()
    transcription = await transcribe_audio(file_bytes, file.filename)
    if not transcription: transcription = "(No audio detected)"

    return await process_submission(session, transcription)

# --- TEXT SUBMISSION (NEW) ---
@app.post("/submit-text", response_model=EvaluationResponse)
async def submit_text(request: TextSubmitRequest):
    session = SESSIONS.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return await process_submission(session, request.text)

# --- SHARED LOGIC ---
async def process_submission(session, user_answer):
    current_q = session["current_q"]
    eval_data = await evaluate_answer(session["domain"], current_q, user_answer)
    
    session["scores"].append(eval_data.get("score", 0))
    session["history"].append({"role": "assistant", "content": current_q})
    session["history"].append({"role": "user", "content": user_answer})
    
    session["full_log"].append({"role": "user", "content": user_answer})
    session["full_log"].append({
        "role": "system_eval", 
        "content": f"Score: {eval_data.get('score')}/10\nFeedback: {eval_data.get('feedback')}"
    })

    session["q_count"] += 1
    next_q = None
    is_over = False
    
    if session["q_count"] <= 5:
        next_q = await generate_question(session["domain"], session["difficulty"], session["history"], session["q_count"])
        session["current_q"] = next_q
        session["full_log"].append({"role": "assistant", "content": next_q})
    else:
        is_over = True
        session["current_q"] = None

    return EvaluationResponse(
        transcription=user_answer,
        score=eval_data.get("score", 0),
        feedback=eval_data.get("feedback", ""),
        improvements=eval_data.get("improvements", ""),
        next_question=next_q,
        is_interview_over=is_over
    )

@app.get("/report/{session_id}", response_model=ReportResponse)
async def get_report(session_id: str):
    session = SESSIONS.get(session_id)
    if not session: raise HTTPException(status_code=404)
        
    summary = await generate_final_report(session["history"])
    avg_score = sum(session["scores"]) / len(session["scores"]) if session["scores"] else 0
    
    return ReportResponse(
        total_score=avg_score,
        summary=summary,
        domain=session["domain"],
        history=session["full_log"]
    )
