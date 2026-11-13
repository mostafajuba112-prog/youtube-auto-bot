import os
from google import genai

# جلب المفتاح المربوط في الـ Secrets
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set!")

client = genai.Client(api_key=api_key)

def generate_video_idea():
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents="Write a short mysterious thriller story idea for a YouTube channel with title and description.",
    )
    print("--- SUCCESS: IDEA GENERATED ---")
    print(response.text)

if __name__ == "__main__":
    generate_video_idea()
