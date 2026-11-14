import os
import asyncio
import re
import time
import urllib.parse
from io import BytesIO

import requests
from PIL import Image

os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"

import google.genai as genai
from moviepy.editor import (
    ImageClip, AudioFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip,
)
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
    print("--- Generating Clean Cinematic Voice via Edge TTS ---")
    voice = "ar-EG-ShakirNeural"
    communicate = edge_tts.Communicate(text, voice, rate="+0%", pitch="-2Hz")
    await communicate.save(output_file)
    print(f"Audio saved to {output_file}")


def generate_story_image(prompt_text, output_path, scene_num):
    print(f"Generating AI image for scene {scene_num}: {prompt_text}")
    full_prompt = (
        f"{prompt_text}, dark cinematic thriller style, mystery atmosphere, "
        f"highly detailed, photorealistic"
    )
    encoded = urllib.parse.quote(full_prompt)

    for attempt in range(4):
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=1080&height=1920&nologo=true&seed={scene_num * 99 + attempt}"
        )
        try:
            r = requests.get(url, timeout=90)
            ctype = r.headers.get("content-type", "")
            print(f"Scene {scene_num} try {attempt + 1}: {r.status_code} {ctype}")
            if r.status_code == 200 and ctype.startswith("image"):
                img = Image.open(BytesIO(r.content)).convert("RGB").resize((1080, 1920))
                img.save(output_path, "JPEG")
                print(f"Image for scene {scene_num} saved successfully.")
                return True
        except Exception as e:
            print(f"Scene {scene_num} error: {e}")
        time.sleep(10 * (attempt + 1))

    print(f"Scene {scene_num} FAILED after all retries.")
    return False


def upload_video_to_youtube(video_path, title, description):
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )

    youtube = build('youtube', 'v3', credentials=creds)

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['قصص غموض', 'shorts', 'ريلز', 'غير قابل للحل', 'اكسبلور', 'رعب'],
            'categoryId': '24',
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%.")

    print(f"Video uploaded successfully! ID: {response.get('id')}")


def make_vertical_clip(path, dur, fallback=None):
    """Use the scene image; if missing, reuse the last good image instead of black."""
    use = None
    if os.path.exists(path) and os.path.getsize(path) > 0:
        use = path
    elif fallback and os.path.exists(fallback) and os.path.getsize(fallback) > 0:
        use = fallback

    if use:
        return ImageClip(use).set_duration(dur)
    return ColorClip(size=(1080, 1920), color=(10, 13, 18), duration=dur)


def main():
    print("--- Starting Automated Mystery Short Production ---")
    os.makedirs("auto_images", exist_ok=True)

    print("--- 1. Generating Script & 5 Scene Prompts ---")
    prompt = """
    اكتب قصة غموض قصيرة جداً ومثيرة (في حدود 40 كلمة) باللغة العربية.
    وأعطني الرد بالشكل التالي بالضبط بدون أي زيادات:
    SCRIPT: [النص الصوتي للقصة هنا]
    PROMPT1: [برومبت بالإنجليزية دقيق للمشهد الأول]
    PROMPT2: [برومبت بالإنجليزية دقيق للمشهد الثاني]
    PROMPT3: [برومبت بالإنجليزية دقيق للمشهد الثالث]
    PROMPT4: [برومبت بالإنجليزية دقيق للمشهد الرابع]
    PROMPT5: [برومبت بالإنجليزية دقيق للمشهد الخامس]
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    raw_response = response.text
    print("AI Response:\n", raw_response)

    script_match = re.search(r'SCRIPT:\s*(.*?)(?=(?:PROMPT1:|$))', raw_response, re.DOTALL)
    p1_match = re.search(r'PROMPT1:\s*(.*?)(?=(?:PROMPT2:|$))', raw_response, re.DOTALL)
    p2_match = re.search(r'PROMPT2:\s*(.*?)(?=(?:PROMPT3:|$))', raw_response, re.DOTALL)
    p3_match = re.search(r'PROMPT3:\s*(.*?)(?=(?:PROMPT4:|$))', raw_response, re.DOTALL)
    p4_match = re.search(r'PROMPT4:\s*(.*?)(?=(?:PROMPT5:|$))', raw_response, re.DOTALL)
    p5_match = re.search(r'PROMPT5:\s*(.*)', raw_response, re.DOTALL)

    raw_script = script_match.group(1).strip() if script_match else raw_response
    p1_text = p1_match.group(1).strip() if p1_match else "Dark mysterious crime scene"
    p2_text = p2_match.group(1).strip() if p2_match else "Detective looking at clues in dark room"
    p3_text = p3_match.group(1).strip() if p3_match else "Suspicious old house at night"
    p4_text = p4_match.group(1).strip() if p4_match else "Secret diary with mysterious symbols"
    p5_text = p5_match.group(1).strip() if p5_match else "Dark thriller suspense ending shadow"

    speech_text = clean_text_for_speech(raw_script)

    print("--- 2. Generating Clean Cinematic Voice via Edge TTS ---")
    audio_file = "reel_audio.mp3"
    asyncio.run(generate_edge_speech(speech_text, audio_file))

    print("--- 3. Generating 5 Story-Related AI Images ---")
    img_paths = [f"auto_images/scene_{i}.jpg" for i in range(1, 6)]
    prompts = [p1_text, p2_text, p3_text, p4_text, p5_text]

    ok_count = 0
    for i, (p, path) in enumerate(zip(prompts, img_paths), start=1):
        if generate_story_image(p, path, i):
            ok_count += 1
        time.sleep(8)  # avoid rate limit between requests
    print(f"Images generated: {ok_count}/5")

    print("--- 4. Assembling Video with Story Images ---")
    audio = AudioFileClip(audio_file)
    total_duration = audio.duration
    scene_duration = total_duration / 5.0

    # first image that actually exists, used as fallback for failed scenes
    fallback = next(
        (p for p in img_paths if os.path.exists(p) and os.path.getsize(p) > 0),
        None,
    )

    clips = [make_vertical_clip(p, scene_duration, fallback) for p in img_paths]
    bg_clip = concatenate_videoclips(clips, method="compose")

    try:
        watermark = TextClip("غير قابل للحل", fontsize=50, color='gold', font="Arial")
        watermark = watermark.set_position(('center', 150)).set_duration(total_duration)
    except Exception:
        watermark = None

    try:
        txt_clip = TextClip(
            speech_text, fontsize=55, color='white', size=(900, None),
            method='caption', align='center', font="Arial",
        )
        txt_clip = txt_clip.set_position('center').set_duration(total_duration)
    except Exception as e:
        print(f"Text rendering note: {e}")
        txt_clip = None

    clips_list = [bg_clip]
    if watermark:
        clips_list.append(watermark)
    if txt_clip:
        clips_list.append(txt_clip)

    final_video = CompositeVideoClip(clips_list, size=(1080, 1920)).set_audio(audio)
    final_video = final_video.set_duration(total_duration)
    output_filename = "final_reel.mp4"
    final_video.write_videofile(
        output_filename,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        ffmpeg_params=["-pix_fmt", "yuv420p"],
    )

    print("--- 5. Uploading to YouTube ---")
    trending_hashtags = "\n\n#shorts #قصص_غموض #اكسبلور #رعب #غموض #مجهول #trending #viral #غير_قابل_للحل"
    full_description = speech_text + trending_hashtags

    upload_video_to_youtube(
        output_filename,
        "لغز جديد 🔍✨ | غير قابل للحل",
        full_description,
    )

    print("--- 6. Cleaning Up Temporary Files ---")
    for f in [audio_file, output_filename] + img_paths:
        if os.path.exists(f):
            os.remove(f)

    print("--- Automated Pipeline Completed Successfully! ---")


if __name__ == "__main__":
    main()
