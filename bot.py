import os
import asyncio
import re
from io import BytesIO
from PIL import Image

os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"

import google.genai as genai
from google.genai import types
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, ColorClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set!")

client = genai.Client(api_key=api_key)

def clean_text_for_speech(text):
    text = re.sub(r'[\*\#\_`~•]', '', text)
    text = re.sub(r'[^\w\s\u0600-\u06FF\.,،؟!\-]', ' ', text)
    return text.strip()

def generate_google_ai_speech(text, output_file):
    print("--- Generating Cinematic Voice via Google AI Studio ---")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"اقرأ النص التالي بصوت تعليقي رجالي عميق جداً، فخم، وبطيء، ومناسب تماماً لأفلام الرعب والغموض والتحقيقات، بدون أي مقدمات أو إضافات، اقرأ النص فقط: {text}",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Fenrir"
                    )
                )
            )
        )
    )
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data and part.inline_data.data:
                with open(output_file, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"Audio saved to {output_file}")
                return True
    raise Exception("Failed to generate audio from Google AI Studio.")

def generate_ai_image(prompt, output_path):
    print(f"Generating AI image for prompt: {prompt}")
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt + ", vertical 9:16 aspect ratio, dark cinematic thriller style, 8k",
            config=dict(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="9:16",
            )
        )
        for generated_image in result.generated_images:
            image = Image.open(BytesIO(generated_image.image.image_bytes))
            image.save(output_path)
            print(f"Image saved to {output_path}")
            return True
    except Exception as e:
        print(f"Image generation error: {e}")
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

    print("--- 1. Generating Script & 5 Visual Prompts ---")
    prompt = """
    اكتب قصة غموض قصيرة جداً ومثيرة (في حدود 40 كلمة) باللغة العربية.
    وأعطني الرد بالشكل التالي بالضبط بدون أي زيادة:
    SCRIPT: [النص الصوتي للقصة هنا]
    PROMPT1: [برومبت بالإنجليزية للمشهد الأول]
    PROMPT2: [برومبت بالإنجليزية للمشهد الثاني]
    PROMPT3: [برومبت بالإنجليزية للمشهد الثالث]
    PROMPT4: [برومبت بالإنجليزية للمشهد الرابع]
    PROMPT5: [برومبت بالإنجليزية للمشهد الخامس]
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
    p1_text = p1_match.group(1).strip() if p1_match else "Dark mysterious thriller scene 1, 8k"
    p2_text = p2_match.group(1).strip() if p2_match else "Dark mysterious thriller scene 2, 8k"
    p3_text = p3_match.group(1).strip() if p3_match else "Dark mysterious thriller scene 3, 8k"
    p4_text = p4_match.group(1).strip() if p4_match else "Dark mysterious thriller scene 4, 8k"
    p5_text = p5_match.group(1).strip() if p5_match else "Dark mysterious thriller scene 5, 8k"

    speech_text = clean_text_for_speech(raw_script)

    print("--- 2. Generating Cinematic Voice via Google AI Studio ---")
    audio_file = "reel_audio.mp3"
    generate_google_ai_speech(speech_text, audio_file)

    print("--- 3. Generating 5 AI Images ---")
    img1_path = "auto_images/scene_1.jpg"
    img2_path = "auto_images/scene_2.jpg"
    img3_path = "auto_images/scene_3.jpg"
    img4_path = "auto_images/scene_4.jpg"
    img5_path = "auto_images/scene_5.jpg"

    generate_ai_image(p1_text, img1_path)
    generate_ai_image(p2_text, img2_path)
    generate_ai_image(p3_text, img3_path)
    generate_ai_image(p4_text, img4_path)
    generate_ai_image(p5_text, img5_path)

    print("--- 4. Assembling Video with 5 Dynamic Images ---")
    audio = AudioFileClip(audio_file)
    total_duration = audio.duration
    scene_duration = total_duration / 5.0

    def make_vertical_clip(path, dur):
        if os.path.exists(path):
            clip = ImageClip(path).set_duration(dur).resize(width=1080)
            if clip.h < 1920:
                clip = clip.resize(height=1920)
            return clip
        else:
            return ColorClip(size=(1080, 1920), color=(20, 24, 33), duration=dur)

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
