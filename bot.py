import os
import requests
import json
from datetime import datetime
from google import genai

# ۱. دریافت کلیدهای امنیتی
API_SPORTS_KEY = os.environ.get("API_SPORTS_KEY")
GEMINI_API_KEYS_STR = os.environ.get("GEMINI_API_KEYS")

if not API_SPORTS_KEY or not GEMINI_API_KEYS_STR:
    print("❌ خطا: کلیدهای API (فوتبال یا جمنای) تنظیم نشده‌اند!")
    exit()

gemini_keys = [k.strip() for k in GEMINI_API_KEYS_STR.split(',') if k.strip()]

BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_SPORTS_KEY}

def predict_with_fallback(mega_prompt):
    """
    اجرای سیستم چندکلیدی با استفاده از پکیج جدید و مدرن گوگل (google-genai)
    """
    for i, key in enumerate(gemini_keys):
        print(f"🔄 در حال تست کلید جمنای شماره {i+1}...")
        try:
            # کدهای آپدیت شده بر اساس استانداردهای جدید گوگل
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model='gemini-1.5-pro',
                contents=mega_prompt
            )
            return response.text
        except Exception as e:
            print(f"⚠️ کلید شماره {i+1} کار نکرد (ارور: {e}). رفتیم سراغ کلید بعدی...")
    
    return "❌ تمام کلیدهای جمنای منقضی شده یا محدود شده‌اند. لطفاً کلید جدید وارد کن."

def get_match_and_predict():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"🔄 در حال دریافت لیست بازی‌های امروز ({today})...")
    
    try:
        response = requests.get(f"{BASE_URL}/fixtures", headers=HEADERS, params={"date": today})
        response.raise_for_status()
        matches = response.json().get("response", [])
        
        if not matches:
            print("📭 امروز هیچ بازی یافت نشد.")
            return

        target_match = matches[0]
        home_team = target_match['teams']['home']['name']
        away_team = target_match['teams']['away']['name']
        league = target_match['league']['name']
        
        print(f"✅ بازی انتخاب شده: {home_team} 🆚 {away_team} در تورنمنت {league}")
        print("🧠 در حال تزریق دیتا به مغز جمنای و پردازش مگاپرامپت...")

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

        ai_response_text = predict_with_fallback(mega_prompt)
        
        print("\n" + "="*50)
        print("🤖 خروجی نهایی اوراکل فوتبال:\n")
        print(ai_response_text)
        print("="*50)

    except Exception as e:
        print(f"❌ خطا در پردازش: {e}")

if __name__ == "__main__":
    get_match_and_predict()
