
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("Available Models:")
    for m in genai.list_models():
        if 'gemini' in m.name:
            print(m.name)
