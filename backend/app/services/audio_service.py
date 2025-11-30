import os
import aiofiles
import google.generativeai as genai
from app.config import settings

MODEL_NAME = "gemini-2.5-flash"

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

async def transcribe_audio(file_bytes: bytes, filename: str) -> str:
    file_path = os.path.join(TEMP_DIR, filename)
    
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            await out_file.write(file_bytes)

        myfile = genai.upload_file(file_path)
        model = genai.GenerativeModel(MODEL_NAME)
        
        result = await model.generate_content_async(
            [myfile, "Generate a verbatim transcript of this audio. Output ONLY the text."]
        )
        
        os.remove(file_path)
        return result.text.strip()
    except Exception as e:
        print(f"Audio Transcription Error: {e}")
        return ""
