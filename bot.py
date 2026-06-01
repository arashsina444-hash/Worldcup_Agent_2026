import os
import requests
from datetime import datetime

# ۱. دریافت کلیدهای امنیتی
API_SPORTS_KEY = os.environ.get("API_SPORTS_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not API_SPORTS_KEY or not GROQ_API_KEY:
    print("❌ خطا: کلیدهای API (فوتبال یا گروق) تنظیم نشده‌اند!")
    exit()

BASE_URL = "https://v3.football.api-sports.io"
HEADERS_SPORTS = {"x-apisports-key": API_SPORTS_KEY}

def predict_with_groq(mega_prompt):
    print("🧠 در حال تزریق دیتا به مغز Llama 3.3 (سرورهای فوق‌سریع Groq)...")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",  # <--- آپدیت به جدیدترین نسل فعال
        "messages": [{"role": "user", "content": mega_prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        if response.status_code == 200:
            return response_json['choices'][0]['message']['content']
        else:
            return f"❌ خطای سرور گروق: {response_json}"
    except Exception as e:
        return f"❌ خطای ارتباطی: {e}"

def get_match_and_predict():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"🔄 در حال دریافت لیست بازی‌های امروز ({today})...")
    
    try:
        response = requests.get(f"{BASE_URL}/fixtures", headers=HEADERS_SPORTS, params={"date": today})
        response.raise_for_status()
        matches = response.json().get("response", [])
        
        if not matches:
            print("📭 امروز هیچ بازی یافت نشد.")
            return

        target_match = matches[0]
        home_team = target_match['teams']['home']['name']
        away_team = target_match['teams']['away']['name']
        league = target_match['league']['name']
        
        print(f"✅ مسابقه: {home_team} 🆚 {away_team} | لیگ: {league}")

        mega_prompt = f"""
        تو یک آنالیزور ارشد و ژورنالیست هیجانی فوتبال هستی که برای یک سندیکای سرمایه‌گذاری کار می‌کنی.
        بازی امروز: {home_team} (میزبان) مقابل {away_team} (مهمان) در لیگ {league}.
        
        قوانینِ مطلقِ تحلیل تو (بر اساس مدل‌های دیکسون-کولز و سیستم Elo ارتقا یافته):
        ۱. مزیت میزبانی: تیم {home_team} به دلیل میزبانی از نظر روانی ۸۰ امتیاز در سیستم Elo جلوتر است. این فشار محیطی را در نظر بگیر.
        ۲. حل معمای مساوی: اگر احساس کردی قدرت دو تیم نزدیک است، شانس نتیجه مساوی (به خصوص ۱-۱) را بسیار بالا ببر.
        ۳. سوگیری داوری: تیم مهمان ({away_team}) تحت فشار استادیوم ممکن است خطای بیشتری کند.
        ۴. لحن تو باید به شدت پرانرژی، کوبنده و مناسبِ یک پست ویروسیِ تلگرام باشد (با استفاده از ایموجی).
        
        خروجی تو باید دقیقاً این فرمت را داشته باشد (بدون کلمات اضافه):
        🔥 تحلیل ژورنالیستی و تاکتیکی بازی (یک پاراگراف هیجانی)
        📊 شانس برد {home_team} / شانس مساوی / شانس برد {away_team} (به درصد)
        🎯 پیش‌بینی دقیق نتیجه نهایی (مثلاً ۲-۱)
        """

        ai_response_text = predict_with_groq(mega_prompt)
        
        print("\n" + "="*50)
        print("🤖 خروجی نهایی اوراکل فوتبال:\n")
        print(ai_response_text)
        print("="*50)

    except Exception as e:
        print(f"❌ خطا در پردازش دیتای فوتبال: {e}")

if __name__ == "__main__":
    get_match_and_predict()
