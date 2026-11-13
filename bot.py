import os
import google.genai as genai
from gtts import gTTS
from moviepy.editor import AudioFileClip, ColorClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# 1. إعدادات مفتاح جيميني
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set!")

client = genai.Client(api_key=api_key)

def upload_video_to_youtube(video_path, title, description):
    # سحب المفاتيح بأمان من بيئة جيثب
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
            'tags': ['قصص غموض', 'shorts', 'ريلز'],
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
    prompt = "اكتب قصة غموض قصيرة جداً ومثيرة (في حدود 30 كلمة) باللغة العربية مع عنوان جذاب ومناسب لفيديوهات الريلز القصيرة."
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    script_text = response.text
    print(script_text)

    print("--- 2. Generating Audio ---")
    audio_file = "reel_audio.mp3"
    tts = gTTS(text=script_text, lang='ar')
    tts.save(audio_file)

    print("--- 3. Rendering Video ---")
    audio = AudioFileClip(audio_file)
    video = ColorClip(size=(1080, 1920), color=(15, 15, 15), duration=audio.duration)
    final_video = video.set_audio(audio)
    
    output_filename = "final_reel.mp4"
    final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")

    print("--- 4. Uploading to YouTube ---")
    upload_video_to_youtube(output_filename, "قصة غموض قصيرة 🔍✨", script_text)

if __name__ == "__main__":
    main()
