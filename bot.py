import os
import google.genai as genai

# إعدادات مفتاح جيميني
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set!")

client = genai.Client(api_key=api_key)

def generate_google_audio(text, output_file):
    print("--- Generating Audio via Google AI ---")
    # نطلب من النموذج توليد محتوى صوتي مباشر بالنبرة المطلوبة
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"اقرأ هذه القصة بصوت تعليقي رجالي عميق، فخم، ومناسب لأفلام الغموض والرعب والتشويق، وبدون أي مقدمات، فقط اقرأ النص التالي: {text}",
        config={
            "response_mime_type": "audio/mp3",
        }
    )
    
    # حفظ الملف الصوتي الناتج مباشرة
    # ملاحظة: البيانات الصوتية بتيجي في أجزاء الـ inline_data الخاصة بالرد
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            with open(output_file, "wb") as f:
                f.write(part.inline_data.data)
            print(f"Audio saved successfully to {output_file}")
            return
            
    raise Exception("Failed to generate audio from Google AI.")
