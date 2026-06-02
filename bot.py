import os
import requests
import time
from datetime import datetime, timedelta

# ۱. دریافت کلیدهای امنیتی
API_SPORTS_KEY = os.environ.get("API_SPORTS_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not API_SPORTS_KEY or not GROQ_API_KEY:
    print("❌ خطا: کلیدهای API تنظیم نشده‌اند!")
    exit()

BASE_URL = "https://v3.football.api-sports.io"
HEADERS_SPORTS = {"x-apisports-key": API_SPORTS_KEY}

# لیگ‌های VIP: لیگ قهرمانان(2)، انگلیس(39)، اسپانیا(140)، ایتالیا(135)، آلمان(78)، فرانسه(61)
TARGET_LEAGUES = [2, 39, 140, 135, 78, 61]

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

def run_monthly_backtest():
    print("⏳ موتور اسکنر ماهانه روشن شد. در حال جمع‌آوری ۵۰ بازی VIP از ماه May 2026...")
    
    start_date = datetime(2026, 5, 1)
    end_date = datetime(2026, 5, 31)
    current_date = start_date
    
    vip_matches = []
    
    # فاز اول: جمع‌آوری ۵۰ بازی از کل ماه
    try:
        while current_date <= end_date and len(vip_matches) < 50:
            date_str = current_date.strftime("%Y-%m-%d")
            
            response = requests.get(f"{BASE_URL}/fixtures", headers=HEADERS_SPORTS, params={"date": date_str})
            matches = response.json().get("response", [])
            
            for m in matches:
                # اگر بازی در لیگ VIP بود و تمام شده بود
                if m['league']['id'] in TARGET_LEAGUES and m['fixture']['status']['short'] in ['FT', 'PEN', 'AET']:
                    vip_matches.append(m)
                    if len(vip_matches) == 50:
                        break
            
            current_date += timedelta(days=1)
            time.sleep(0.5) # توقف کوتاه برای فشار نیاوردن به API
            
        if not vip_matches:
            print("📭 هیچ بازی VIP در این ماه یافت نشد!")
            return

        print(f"✅ تعداد {len(vip_matches)} بازی VIP با موفقیت جمع‌آوری شد.\n" + "="*60)

        # فاز دوم: شروع پیش‌بینی کورکورانه (Blind Test)
        for index, match in enumerate(vip_matches):
            fixture_id = match['fixture']['id']
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            league = match['league']['name']
            match_date = match['fixture']['date'][:10]
            
            # استخراج نتیجه واقعی برای مقایسه (ارسال نمی‌شود)
            home_goals = match['goals']['home']
            away_goals = match['goals']['away']
            actual_result = f"{home_goals} - {away_goals}"

            print(f"\n[{index+1}/50] 🎯 تاریخ: {match_date} | {home_team} 🆚 {away_team} ({league})")

            # دریافت دیتای Predictions از ماشین
            pred_response = requests.get(f"{BASE_URL}/predictions", headers=HEADERS_SPORTS, params={"fixture": fixture_id})
            pred_data = pred_response.json().get("response", [])
            
            stats_text = "دیتای آماری در دسترس نیست."
            if pred_data:
                percent = pred_data[0].get('predictions', {}).get('percent', {})
                stats_text = f"شانس ماشین: برد میزبان {percent.get('home', 'N/A')} | مساوی {percent.get('draw', 'N/A')} | برد مهمان {percent.get('away', 'N/A')}"

            # ساخت پرامپت
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

            # شلیک به هوش مصنوعی
            ai_prediction = predict_with_groq(mega_prompt)
            
            # نمایش نتیجه
            print(f"🤖 پیش‌بینی هوش مصنوعی: {ai_prediction.strip()}")
            print(f"📺 نتیجه واقعی در زمین:  {actual_result}")
            print("-" * 50)
            
            time.sleep(3) # توقف برای جلوگیری از ارور محدودیت سرعت سرور هوش مصنوعی

        print("\n🏆 بک‌تستِ سنگین ۵۰ بازی ماه گذشته تمام شد! حالا درصد وین‌ریت را محاسبه کن.")

    except Exception as e:
        print(f"❌ خطا در اجرای اسکنر ماهانه: {e}")

if __name__ == "__main__":
    run_monthly_backtest()
