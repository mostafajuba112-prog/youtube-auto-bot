import os
import google.genai as genai
from google.genai import types

# تأكد إن المفتاح متعرّف
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def generate_google_ai_speech(text, output_file):
    print("--- Generating Cinematic Voice via Google AI Studio ---")
    
    # طلب توليد الصوت من نموذج جيميني مع تحديد نبرة وصوت عميق (مثل Fenrir أو Puck)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"اقرأ النص التالي بصوت تعليقي رجالي عميق جداً، فخم، وبطيء، ومناسب تماماً لأفلام الرعب والغموض والتحقيقات، بدون أي مقدمات أو إضافات، اقرأ النص فقط: {text}",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Fenrir" # صوت رجالي عميق وقوي يناسب الغموض
                    )
                )
            )
        )
    )
    
    # استخراج ملف الصوت الناتج وحفظه بصيغة MP3
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data and part.inline_data.data:
                with open(output_file, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"Audio successfully generated and saved to {output_file}")
                return True
                
    raise Exception("Failed to generate audio from Google AI Studio.")
