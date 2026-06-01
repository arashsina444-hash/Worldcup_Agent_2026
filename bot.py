import os
import requests
from datetime import datetime

# ۱. دریافت کلیدهای امنیتی
API_SPORTS_KEY = os.environ.get("API_SPORTS_KEY")
GEMINI_API_KEYS_STR = os.environ.get("GEMINI_API_KEYS")

if not API_SPORTS_KEY or not GEMINI_API_KEYS_STR:
    print("❌ خطا: کلیدهای API تنظیم نشده‌اند!")
    exit()

gemini_keys = [k.strip() for k in GEMINI_API_KEYS_STR.split(',') if k.strip()]
# لیست تمام مدل‌های ممکن برای دور زدن محدودیت‌های گوگل
models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]

BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_SPORTS_KEY}

def predict_with_rest_api(mega_prompt):
    """
    ارتباط مستقیم با هسته گوگل بدون نیاز به کتابخانه‌های باگ‌دارِ پایتون
    """
    payload = {
        "contents": [{"parts": [{"text": mega_prompt}]}]
    }
    
    for i, key in enumerate(gemini_keys):
        print(f"\n🔑 در حال تست کلید شماره {i+1}...")
        for model in models_to_try:
            print(f"  🔄 تست مدل: {model} ...", end=" ")
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            
            try:
                response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
                data = response.json()
                
                if response.status_code == 200:
                    print("✅ موفق!")
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    error_msg = data.get('error', {}).get('message', 'Unknown Error')
                    print(f"❌ مسدود (ارور: {response.status_code})")
            except Exception as e:
                print(f"❌ خطای ارتباطی: {e}")
                
    return "❌ تمام ترکیب‌های کلید و مدل با شکست مواجه شدند. گوگل دسترسی این کلیدها را کاملاً بسته است."

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
        
        print(f"✅ مسابقه: {home_team} 🆚 {away_team} | لیگ: {league}")
        print("🧠 در حال تزریق دیتا به مغز جمنای (ارتباط مستقیم ابری)...")

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

        ai_response_text = predict_with_rest_api(mega_prompt)
        
        print("\n" + "="*50)
        print("🤖 خروجی نهایی اوراکل فوتبال:\n")
        print(ai_response_text)
        print("="*50)

    except Exception as e:
        print(f"❌ خطا در پردازش دیتای فوتبال: {e}")

if __name__ == "__main__":
    get_match_and_predict()
