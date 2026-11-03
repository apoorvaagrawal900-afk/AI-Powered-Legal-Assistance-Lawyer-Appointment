import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    raise RuntimeError('GEMINI_API_KEY is missing.')

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Reply with only: Connection successful"
    )

    print(response.text)

except Exception as exc:
    print(f"Error type: {type(exc).__name__}")
    print(f"Error details: {exc}")