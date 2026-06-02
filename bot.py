import os
import requests
from datetime import datetime

# ۱. دریافت کلیدهای امنیتی
API_SPORTS_KEY = os.environ.get("API_SPORTS_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not API_SPORTS_KEY or not GROQ_API_KEY:
    print("❌ خطا: کلیدهای API تنظیم نشده‌اند!")
    exit()

BASE_URL = "https://v3.football.api-sports.io"
HEADERS_SPORTS = {"x-apisports-key": API_SPORTS_KEY}

def predict_with_groq(mega_prompt):
    print("🧠 در حال پردازش ترکیبیِ دیتا (ریاضی + روانشناسی) در مغز Llama 3.3...")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
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
        # فاز اول: دریافت لیست بازی‌ها
        response = requests.get(f"{BASE_URL}/fixtures", headers=HEADERS_SPORTS, params={"date": today})
        response.raise_for_status()
        matches = response.json().get("response", [])
        
        # ⚠️ فیلتر لیگ‌ها موقتاً برداشته شد تا روی هر بازی موجود تست کنیم
        valid_matches = matches
        
        if not valid_matches:
            print("📭 امروز هیچ بازی در هیچ‌کجای دنیا یافت نشد.")
            return

        # انتخاب اولین بازی موجود
        target_match = valid_matches[0]
        fixture_id = target_match['fixture']['id']
        home_team = target_match['teams']['home']['name']
        away_team = target_match['teams']['away']['name']
        league = target_match['league']['name']
        
        print(f"✅ مسابقه تست یافت شد: {home_team} 🆚 {away_team} | تورنمنت: {league}")
        print(f"📊 در حال استخراج دیتای پیشرفته آماری و یادگیری ماشین...")

        # فاز دوم: استخراج دیتای Predictions از API-Sports
        pred_response = requests.get(f"{BASE_URL}/predictions", headers=HEADERS_SPORTS, params={"fixture": fixture_id})
        pred_data = pred_response.json().get("response", [])
        
        stats_text = "دیتای آماری پیشرفته برای این بازی در دسترس نیست."
        if pred_data:
            prediction_info = pred_data[0].get('predictions', {})
            percent = prediction_info.get('percent', {})
            advice = prediction_info.get('advice', 'نامشخص')
            
            stats_text = f"""
            دیتای خام استخراج شده از مدل‌های ریاضی (Machine Learning):
            - شانس برد میزبان ({home_team}): {percent.get('home', 'N/A')}
            - شانس مساوی: {percent.get('draw', 'N/A')}
            - شانس برد مهمان ({away_team}): {percent.get('away', 'N/A')}
            - توصیه ماشینی API-Sports: {advice}
            """

        # فاز سوم: ساخت مگاپرامپت (ترکیب ماشین + ذهن انسان)
        mega_prompt = f"""
        تو یک آنالیزور ارشد و استراتژیست فوتبال برای یک سوپراپِ پیش‌بینیِ حرفه‌ای هستی.
        بازی امروز: {home_team} (میزبان) 🆚 {away_team} (مهمان) در تورنمنت {league}.
        
        {stats_text}
        
        قوانینِ مطلقِ تحلیل تو (بر اساس مدل‌های دیکسون-کولز و روانشناسی فوتبال):
        ۱. دیتای ریاضیِ بالا را پایه و اساس قرار بده، اما آن را با پارامترهای زیر کالیبره کن:
        ۲. مزیت میزبانی محتاطانه: به تیم میزبان فقط ۵۰ امتیاز Elo (نه بیشتر) برای فشار استادیوم و سوگیری داوری بده.
        ۳. قانون شجاعت در مساوی: اگر درصدهای بالا به هم نزدیک بودند (مثلاً تفاوت شانس برد دو تیم کمتر از ۱۵٪ بود)، جسارت داشته باش و شانس نتیجه مساوی (به خصوص ۱-۱ یا ۰-۰) را به شدت بالا ببر. در تله‌ی پیش‌بینی برد برای تیم میزبان نیفت.
        ۴. لحن تو باید هیجانی، کوبنده، دارای ایموجی و مناسب برای کاربران یک اپلیکیشن VIP پولی باشد.
        
        خروجی تو باید دقیقاً این فرمت را داشته باشد (بدون حاشیه):
        🔥 تحلیل ژورنالیستی و تاکتیکی بازی (با اشاره هوشمندانه به آمارهای ماشین و وضعیت روانی)
        📊 شانس برد {home_team} / شانس مساوی / شانس برد {away_team} (درصدهای نهایی و کالیبره شده خودت را بنویس)
        🎯 پیش‌بینی دقیق نتیجه نهایی (مثلاً ۱-۱)
        """

        ai_response_text = predict_with_groq(mega_prompt)
        
        print("\n" + "="*60)
        print("🤖 خروجی نهایی موتور سوپراپ (حالت تست بدون فیلتر):\n")
        print(ai_response_text)
        print("="*60)

    except Exception as e:
        print(f"❌ خطا در پردازش سیستم: {e}")

if __name__ == "__main__":
    get_match_and_predict()
