import os
from google import genai
from gtts import gTTS

# جلب مفتاح الـ API بأمان
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set!")

client = genai.Client(api_key=api_key)

def generate_reel_content():
    # 1. توليد سيناريو قصير ومثير للريلز بواسطة جيميني
    prompt = "اكتب قصة غموض قصيرة جداً (في حدود 30 كلمة) ومثيرة ومناسبة لفيديوهات الريلز القصيرة باللغة العربية."
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    script_text = response.text
    print("--- 1. Reel Script Generated ---")
    print(script_text)

    # حفظ النص في ملف نصي
    with open("story_script.txt", "w", encoding="utf-8") as f:
        f.write(script_text)

    # 2. تحويل النص إلى ملف صوتي للريلز
    tts = gTTS(text=script_text, lang='ar')
    audio_file = "reel_audio.mp3"
    tts.save(audio_file)
    print(f"--- 2. Audio Saved: {audio_file} ---")

if __name__ == "__main__":
    generate_reel_content()
