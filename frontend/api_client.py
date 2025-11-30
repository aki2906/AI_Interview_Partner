import requests

API_URL = "http://localhost:8000"

def start_interview_session(domain, difficulty):
    try:
        response = requests.post(f"{API_URL}/start", json={"domain": domain, "difficulty": difficulty})
        if response.status_code != 200: return {"error": response.text}
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def submit_audio_response(session_id, audio_bytes):
    files = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
    data = {'session_id': session_id}
    try:
        response = requests.post(f"{API_URL}/submit-audio", data=data, files=files)
        if response.status_code != 200: return {"error": response.text}
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def submit_text_response(session_id, text_answer):
    try:
        # Calls the new /submit-text endpoint
        response = requests.post(f"{API_URL}/submit-text", json={"session_id": session_id, "text": text_answer})
        if response.status_code != 200: return {"error": response.text}
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_final_report(session_id):
    try:
        response = requests.get(f"{API_URL}/report/{session_id}")
        return response.json()
    except:
        return {}
