import os
import google.generativeai as genai

# جلب مفتاح الـ API
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set!")

genai.configure(api_key=api_key)

def generate_video_idea():
    # استخدام النموذج السريع
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = "Write a short mysterious thriller story idea for a YouTube channel with title and description in Arabic."
    response = model.generate_content(prompt)
    print("--- SUCCESS: IDEA GENERATED ---")
    print(response.text)

if __name__ == "__main__":
    generate_video_idea()
