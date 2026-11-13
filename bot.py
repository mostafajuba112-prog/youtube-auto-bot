import os
from google import genai
from gtts import gTTS
from moviepy.editor import AudioFileClip, ColorClip

# جلب مفتاح الـ API
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set!")

client = genai.Client(api_key=api_key)

def build_reel():
    # 1. توليد قصة غموض قصيرة ومثيرة
    prompt = "اكتب قصة غموض قصيرة جداً (في حدود 30 كلمة) ومثيرة ومناسبة لفيديوهات الريلز القصيرة باللغة العربية."
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    script_text = response.text
    print("--- 1. Script Generated ---")
    print(script_text)

    # حفظ النص في ملف
    with open("story_script.txt", "w", encoding="utf-8") as f:
        f.write(script_text)

    # 2. تحويل النص لصوت
    audio_file = "reel_audio.mp3"
    tts = gTTS(text=script_text, lang='ar')
    tts.save(audio_file)
    print("--- 2. Audio Generated ---")

    # 3. دمج الصوت مع خلفية مرئية لتشكيل فيديو الريلز (mp4)
    print("--- 3. Building Video ---")
    audio_clip = AudioFileClip(audio_file)
    
    # إنشاء خلفية داكنة بمقاسات الريلز (عرض 1080 في طول 1920) وبنفس مدة الصوت بالضبط
    video_clip = ColorClip(size=(1080, 1920), color=(15, 15, 15), duration=audio_clip.duration)
    
    # دمج الصوت مع الفيديو
    final_clip = video_clip.set_audio(audio_clip)
    
    # حفظ الفيديو النهائي بصيغة mp4
    output_video = "final_reel.mp4"
    final_clip.write_videofile(
        output_video,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )
    print(f"--- 4. Video Created Successfully: {output_video} ---")

if __name__ == "__main__":
    build_reel()
