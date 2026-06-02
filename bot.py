import os
import requests
import time

# ۱. دریافت کلیدهای امنیتی
API_SPORTS_KEY = os.environ.get("API_SPORTS_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not API_SPORTS_KEY or not GROQ_API_KEY:
    print("❌ خطا: کلیدهای API تنظیم نشده‌اند!")
    exit()

BASE_URL = "https://v3.football.api-sports.io"
HEADERS_SPORTS = {"x-apisports-key": API_SPORTS_KEY}

# لیگ‌های VIP (انگلیس، اسپانیا، ایتالیا، آلمان، فرانسه)
TARGET_LEAGUES = [39, 140, 135, 78, 61]

# ⚠️ تاریخ ماشین زمان (یک روز شلوغ در ماه گذشته که بازی‌های مهمی داشته)
PAST_DATE = "2026-05-02" 

def predict_with_groq(mega_prompt):
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
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"❌ خطای سرور گروق"
    except Exception as e:
        return f"❌ خطای ارتباطی"

def run_vip_backtest():
    print(f"⏳ ماشین زمان روشن شد. در حال سفر به تاریخ: {PAST_DATE} ...")
    
    try:
        # ۱. دریافت تمام بازی‌های آن روز
        response = requests.get(f"{BASE_URL}/fixtures", headers=HEADERS_SPORTS, params={"date": PAST_DATE})
        matches = response.json().get("response", [])
        
        # ۲. فیلتر کردن فقط بازی‌های VIP و بازی‌هایی که تمام شده‌اند (FT)
        vip_matches = [m for m in matches if m['league']['id'] in TARGET_LEAGUES and m['fixture']['status']['short'] in ['FT', 'PEN', 'AET']]
        
        if not vip_matches:
            print("📭 در این تاریخ هیچ بازی VIP تمام‌شده‌ای یافت نشد. تاریخ را در کد عوض کن.")
            return

        # انتخاب حداکثر ۵۰ بازی (برای جلوگیری از طولانی شدن بیش از حد اکشن گیت‌هاب)
        test_matches = vip_matches[:50]
        print(f"✅ تعداد {len(test_matches)} بازی VIP برای بک‌تستِ سنگین انتخاب شد.\n" + "="*60)

        for index, match in enumerate(test_matches):
            fixture_id = match['fixture']['id']
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            league = match['league']['name']
            
            # ۳. استخراج نتیجه واقعی (فقط برای نمایش به تو، نه ارسال به ربات!)
            home_goals = match['goals']['home']
            away_goals = match['goals']['away']
            actual_result = f"{home_goals} - {away_goals}"

            print(f"\n[{index+1}/{len(test_matches)}] 🎯 در حال آنالیز: {home_team} 🆚 {away_team} ({league})")

            # ۴. دریافت دیتای Predictions آماری از ماشین
            pred_response = requests.get(f"{BASE_URL}/predictions", headers=HEADERS_SPORTS, params={"fixture": fixture_id})
            pred_data = pred_response.json().get("response", [])
            
            stats_text = "دیتای آماری در دسترس نیست."
            if pred_data:
                percent = pred_data[0].get('predictions', {}).get('percent', {})
                stats_text = f"شانس ماشین: برد میزبان {percent.get('home', 'N/A')} | مساوی {percent.get('draw', 'N/A')} | برد مهمان {percent.get('away', 'N/A')}"

            # ۵. ساخت پرامپت (بدون لو دادن نتیجه واقعی)
            mega_prompt = f"""
            تو یک آنالیزور ارشد فوتبال هستی.
            بازی: {home_team} (میزبان) 🆚 {away_team} (مهمان).
            دیتای ماشین: {stats_text}
            
            قوانین:
            ۱. مزیت میزبانی محتاطانه (۵۰ امتیاز).
            ۲. جسارت در مساوی اگر درصدها نزدیک است.
            ۳. به هیچ وجه نتیجه واقعی بازی را حدس نزن. فقط پیش‌بینی کن.
            
            فقط و فقط یک خط خروجی بده:
            پیش‌بینی دقیق نتیجه نهایی (مثلاً ۱-۰ یا ۱-۱) را بنویس.
            """

            # ۶. شلیک به موتور هوش مصنوعی
            ai_prediction = predict_with_groq(mega_prompt)
            
            # ۷. مقایسه در لحظه
            print(f"🤖 پیش‌بینی هوش مصنوعی: {ai_prediction.strip()}")
            print(f"📺 نتیجه واقعی در زمین:  {actual_result}")
            print("-" * 50)
            
            # توقف ۳ ثانیه‌ای برای جلوگیری از مسدود شدن API
            time.sleep(3)

        print("\n🏆 بک‌تستِ سنگین ۵۰ بازی تمام شد! حالا درصد وین‌ریت را محاسبه کن.")

    except Exception as e:
        print(f"❌ خطا در اجرای ماشین زمان: {e}")

if __name__ == "__main__":
    run_vip_backtest()
