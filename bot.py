import os
import asyncio
import re

# ضبط إعدادات الـ Ffmpeg لتعمل تلقائياً داخل بيئة لينكس
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"

import google.genai as genai
import edge_tts
from moviepy.editor import AudioFileClip, ColorClip, TextClip, CompositeVideoClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# 1. إعدادات مفتاح جيميني
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set!")

client = genai.Client(api_key=api_key)

def clean_text_for_speech(text):
    # إزالة النجوم (الماركداون) والرموز والإيموجي التي تجعل الـ TTS ينطق كلمات غريبة مثل "نجمة"
    text = re.sub(r'[\*\#\_`~•]', '', text)
    # الاحتفاظ فقط بالحروف العربية والإنجليزية والأرقام وعلامات الترقيم الأساسية
    text = re.sub(r'[^\w\s\u0600-\u06FF\.,،؟!\-]', ' ', text)
    return text.strip()

async def generate_edge_audio(text, output_file):
    voice = "ar-SA-HamedNeural"  # صوت سعودي عميق وفخم جداً للغموض والتشويق
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def upload_video_to_youtube(video_path, title, description):
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )

    youtube = build('youtube', 'v3', credentials=creds)

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['قصص غموض', 'shorts', 'ريلز', 'غير قابل للحل', 'اكسبلور', 'رعب'],
            'categoryId': '24'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%.")

    print(f"Video uploaded successfully! ID: {response.get('id')}")

def main():
    print("--- 1. Generating Mystery Script ---")
    prompt = "اكتب قصة غموض قصيرة جداً ومثيرة (في حدود 25 كلمة) باللغة العربية بدون أي رموز أو علامات تزيين، مناسبة لفيديوهات الريلز."
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    raw_script_text = response.text
    print("Raw Script:", raw_script_text)

    # تنظيف النص تماماً من أي رموز أو نجوم قد يقرأها الصوت بشكل خاطئ
    speech_text = clean_text_for_speech(raw_script_text)
    print("Cleaned Speech Text:", speech_text)

    print("--- 2. Generating Cinematic Audio (Edge-TTS) ---")
    audio_file = "reel_audio.mp3"
    asyncio.run(generate_edge_audio(speech_text, audio_file))

    print("--- 3. Rendering Video with Text & Background ---")
    audio = AudioFileClip(audio_file)
    
    # خلفية سينمائية داكنة
    bg_clip = ColorClip(size=(1080, 1920), color=(20, 24, 33), duration=audio.duration)
    
    # اسم القناة كعلامة تجارية
    try:
        watermark = TextClip("غير قابل للحل", fontsize=50, color='gold', font="Arial")
        watermark = watermark.set_position(('center', 150)).set_duration(audio.duration)
    except:
        watermark = None

    # نص القصة في المنتصف (نعرض النص النظيف بدون رموز)
    try:
        txt_clip = TextClip(speech_text, fontsize=60, color='white', size=(900, None), method='caption', align='center', font="Arial")
        txt_clip = txt_clip.set_position('center').set_duration(audio.duration)
    except Exception as e:
        print(f"Text rendering note: {e}")
        txt_clip = None

    clips_list = [bg_clip]
    if watermark:
        clips_list.append(watermark)
    if txt_clip:
        clips_list.append(txt_clip)

    final_video = CompositeVideoClip(clips_list).set_audio(audio)
    
    output_filename = "final_reel.mp4"
    final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")

    print("--- 4. Uploading to YouTube with Trending Hashtags ---")
    trending_hashtags = "\n\n#shorts #قصص_غموض #اكسبلور #رعب #غموض #مجهول #trending #viral #غير_قابل_للحل"
    full_description = raw_script_text + trending_hashtags

    upload_video_to_youtube(
        output_filename, 
        "قصة غموض قصيره 🔍✨ | غير قابل للحل", 
        full_description
    )

if __name__ == "__main__":
    main()
