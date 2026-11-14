import os
import asyncio
import re
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter

os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"

import google.genai as genai
from google.genai import types
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import edge_tts

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set!")

client = genai.Client(api_key=api_key)

def clean_text_for_speech(text):
    text = re.sub(r'[\*\#\_`~•]', '', text)
    text = re.sub(r'[^\w\s\u0600-\u06FF\.,،؟!\-]', ' ', text)
    return text.strip()

async def generate_edge_speech(text, output_file):
    print("--- Generating Cinematic Voice via Edge TTS ---")
    voice = "ar-EG-ShakirNeural"
    communicate = edge_tts.Communicate(text, voice, rate="+0%", pitch="-10Hz")
    await communicate.save(output_file)
    print(f"Audio saved to {output_file}")

def generate_cinematic_background(output_path, index):
    print(f"Generating professional cinematic background for scene {index}...")
    # إنشاء لوحة رأسية مقاس ريلز 9:16 بألوان داكنة وغامضة
    img = Image.new('RGB', (1080, 1920), color=(10, 13, 18))
    draw = ImageDraw.Draw(img)
    
    # رسم تأثيرات ضوئية وتدرجات سينمائية عشوائية تمنح طابع الغموض
    for _ in range(20):
        x1 = random.randint(-300, 1100)
        y1 = random.randint(-300, 1700)
        x2 = x1 + random.randint(400, 900)
        y2 = y1 + random.randint(400, 900)
        # ألوان تميل للأزرق الداكن والرمادي والبنفسجي الخافت لأجواء الجريمة والتحقيق
        color = (random.randint(10, 35), random.randint(15, 40), random.randint(45, 95))
        draw.ellipse([x1, y1, x2, y2], fill=color)
        
    # دمج وتنعيم المؤثرات لتخرج بصورة سينمائية احترافية ناعمة
    img = img.filter(ImageFilter.GaussianBlur(90))
    img.save(output_path)
    print(f"Cinematic background saved to {output_path}")

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
    print("--- Starting Automated Mystery Short Production ---")
    os.makedirs("auto_images", exist_ok=True)

    print("--- 1. Generating Mystery Script via Gemini ---")
    prompt = "اكتب قصة غموض قصيرة جداً ومثيرة (في حدود 40 كلمة) باللغة العربية للتعليق الصوتي فقط بدون أي عناوين أو مقدمات."
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    raw_script = response.text.strip()
    speech_text = clean_text_for_speech(raw_script)

    print("--- 2. Generating Cinematic Voice via Edge TTS ---")
    audio_file = "reel_audio.mp3"
    asyncio.run(generate_edge_speech(speech_text, audio_file))

    print("--- 3. Generating 5 Cinematic Visual Scenes Locally ---")
    img1_path = "auto_images/scene_1.jpg"
    img2_path = "auto_images/scene_2.jpg"
    img3_path = "auto_images/scene_3.jpg"
    img4_path = "auto_images/scene_4.jpg"
    img5_path = "auto_images/scene_5.jpg"

    generate_cinematic_background(img1_path, 1)
    generate_cinematic_background(img2_path, 2)
    generate_cinematic_background(img3_path, 3)
    generate_cinematic_background(img4_path, 4)
    generate_cinematic_background(img5_path, 5)

    print("--- 4. Assembling Video with 5 Dynamic Scenes ---")
    audio = AudioFileClip(audio_file)
    total_duration = audio.duration
    scene_duration = total_duration / 5.0

    def make_vertical_clip(path, dur):
        if os.path.exists(path):
            return ImageClip(path).set_duration(dur)
        return ImageClip(img1_path).set_duration(dur)

    c1 = make_vertical_clip(img1_path, scene_duration)
    c2 = make_vertical_clip(img2_path, scene_duration)
    c3 = make_vertical_clip(img3_path, scene_duration)
    c4 = make_vertical_clip(img4_path, scene_duration)
    c5 = make_vertical_clip(img5_path, scene_duration + (total_duration - (scene_duration * 5)))

    bg_clip = concatenate_videoclips([c1, c2, c3, c4, c5])

    try:
        watermark = TextClip("غير قابل للحل", fontsize=50, color='gold', font="Arial")
        watermark = watermark.set_position(('center', 150)).set_duration(total_duration)
    except:
        watermark = None

    try:
        txt_clip = TextClip(speech_text, fontsize=55, color='white', size=(900, None), method='caption', align='center', font="Arial")
        txt_clip = txt_clip.set_position('center').set_duration(total_duration)
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

    print("--- 5. Uploading to YouTube ---")
    trending_hashtags = "\n\n#shorts #قصص_غموض #اكسبلور #رعب #غموض #مجهول #trending #viral #غير_قابل_للحل"
    full_description = speech_text + trending_hashtags

    upload_video_to_youtube(
        output_filename,
        "لغز جديد 🔍✨ | غير قابل للحل",
        full_description
    )

    print("--- 6. Cleaning Up Temporary Files ---")
    for f in [audio_file, output_filename, img1_path, img2_path, img3_path, img4_path, img5_path]:
        if os.path.exists(f):
            os.remove(f)

    print("--- Automated Pipeline Completed Successfully! ---")

if __name__ == "__main__":
    main()
