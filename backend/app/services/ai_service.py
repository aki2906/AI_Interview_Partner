import json
import google.generativeai as genai
from app.config import settings
from app.utils.prompts import INTERVIEWER_SYSTEM_PROMPT, EVALUATOR_SYSTEM_PROMPT

MODEL_NAME = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

async def generate_question(domain: str, difficulty: str, history: list, q_num: int) -> str:
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history])
    
    prompt = f"""
    {INTERVIEWER_SYSTEM_PROMPT.format(domain=domain, difficulty=difficulty, q_num=q_num, total_q=5)}
    
    Previous Chat History:
    {history_text}
    
    Task: Generate the next interview question now.
    """
    
    response = await model.generate_content_async(prompt)
    return response.text.strip()

async def evaluate_answer(domain: str, question: str, answer: str) -> dict:
    prompt = f"""
    {EVALUATOR_SYSTEM_PROMPT}
    
    Domain: {domain}
    Question: {question}
    Candidate Answer: {answer}
    
    Return STRICT JSON:
    {{
        "score": <int 0-10>,
        "feedback": "<string>",
        "improvements": "<string>"
    }}
    """
    
    response = await model.generate_content_async(
        prompt, 
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)

async def generate_final_report(history: list) -> str:
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history])
    prompt = f"Summarize this interview performance, highlight strengths/weaknesses, and give career advice based on this transcript:\n{history_text}"
    response = await model.generate_content_async(prompt)
    return response.text
