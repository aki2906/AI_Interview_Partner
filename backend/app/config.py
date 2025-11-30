import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# ROBUST PATH FINDING
# 1. Get the path of this config file
current_file = Path(__file__).resolve()

# 2. Calculate the ROOT directory (3 levels up: app -> backend -> ROOT)
root_dir = current_file.parent.parent.parent

# 3. Define the path to .env
env_path = root_dir / ".env"

print(f"🔍 Config is looking for .env at: {env_path}")

# 4. Load it
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("✅ .env file found and loaded.")
else:
    # Fallback: try loading from current working directory
    print(f"⚠️ .env not found at {env_path}, trying current directory...")
    load_dotenv()

class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

settings = Settings()

# 5. Configure Google GenAI
if not settings.GOOGLE_API_KEY:
    print("❌ CRITICAL ERROR: GOOGLE_API_KEY is missing from environment.")
    print("   Make sure your .env file is in the ROOT folder 'AI_Interview_Partner - Copy'")
    print("   and contains: GOOGLE_API_KEY=AIzaSy...")
else:
    print(f"✅ API Key successfully loaded: {settings.GOOGLE_API_KEY[:5]}...")
    genai.configure(api_key=settings.GOOGLE_API_KEY)
