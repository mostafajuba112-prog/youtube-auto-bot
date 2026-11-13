import os
from google import genai
from gtts import gTTS
from moviepy.editor import AudioFileClip, ColorClip

# (مكتبات رفع يوتيوب اللي هنفعلها بربط المفاتيح)
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set!")

client = genai.Client(api_key=api_key)

def build_and_upload_reel():
    # 1. توليد قصة غموض قصيرة
    prompt = "اكتب قصة غموض قصيرة جداً (في حدود 30 كلمة) ومثيرة ومناسبة لفيديوهات الريلز القصيرة باللغة العربية مع عنوان جذاب."
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    script_text = response.text
    print("--- 1. Script Generated ---")

    # 2. تحويل النص لصوت
    audio_file = "reel_audio.mp3"
    tts = gTTS(text=script_text, lang='ar')
    tts.save(audio_file)
    print("--- 2. Audio Generated ---")

    # 3. بناء الفيديو المرئي (mp4)
    print("--- 3. Building Video ---")
    audio_clip = AudioFileClip(audio_file)
    video_clip = ColorClip(size=(1080, 1920), color=(15, 15, 15), duration=audio_clip.duration)
    final_clip = video_clip.set_audio(audio_clip)
    
    output_video = "final_reel.mp4"
    final_clip.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")
    print(f"--- 4. Video Created: {output_video} ---")

    # 4. خطوة الرفع على يوتيوب (هتشتغل بمجرد ربط مفاتيح الأمان في GitHub Secrets)
    # youtube_upload(output_video, script_text[:50])

if __name__ == "__main__":
    build_and_upload_vault = build_and_upload_reel()
