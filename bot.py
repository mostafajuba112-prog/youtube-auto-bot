import os
import google.generativeai as genai

# جلب مفتاح الـ API وتكوينه
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set!")

genai.configure(api_key=api_key)

def generate_video_idea():
    # استخدام النموذج القياسي السريع
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = "اكتب لي فكرة قصة غموض أو جريمة تشويقية قصيرة ومثيرة للقناة، مع العنوان والوصف المناسب ليوتيوب."
    response = model.generate_content(prompt)
    print("--- الفكرة والسيناريو المقترح ---")
    print(response.text)

if __name__ == "__main__":
    generate_video_idea()
