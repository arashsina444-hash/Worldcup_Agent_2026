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

# لیگ‌های VIP: لیگ قهرمانان(2)، انگلیس(39)، اسپانیا(140)، ایتالیا(135)، آلمان(78)، فرانسه(61)
TARGET_LEAGUES = [2, 39, 140, 135, 78, 61]
SEASON = 2025 # فصل فوتبالی که در می ۲۰۲۶ در حال پایان بوده است
MAX_TESTS = 15 # محدودیت برای نسوزاندن سهمیه ۱۰۰ ریکوئست روزانه اکانت رایگان

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

def run_optimized_backtest():
    print("⏳ موتور اسکنر بهینه (ضد-بلاک) روشن شد. در حال استخراج دیتای فصل...")
    vip_matches = []
    
    try:
        # فاز اول: دریافت یکجای دیتا برای جلوگیری از مسدود شدن (Rate Limit)
        for league_id in TARGET_LEAGUES:
            print(f"📡 در حال دریافت دیتای کامل لیگ {league_id}...")
            response = requests.get(f"{BASE_URL}/fixtures", headers=HEADERS_SPORTS, params={"league": league_id, "season": SEASON})
            matches = response.json().get("response", [])
            
            for m in matches:
                date_str = m['fixture']['date']
                status = m['fixture']['status']['short']
                # فیلتر کردن فقط بازی‌های ماه May 2026 که به اتمام رسیده‌اند
                if "2026-05" in date_str and status in ['FT', 'PEN', 'AET']:
                    vip_matches.append(m)
            
            # ⚠️ ترمز ۶ ثانیه‌ای برای رعایت قانون (حداکثر ۱۰ ریکوئست در دقیقه)
            time.sleep(6.5) 
            
        if not vip_matches:
            print("📭 هیچ بازی VIP در این بازه یافت نشد!")
            return

        # مرتب‌سازی بازی‌ها بر اساس تاریخ
        vip_matches.sort(key=lambda x: x['fixture']['date'])
        test_matches = vip_matches[:MAX_TESTS]
        
        print(f"✅ تعداد {len(vip_matches)} بازی یافت شد. برای حفظ سهمیه روزانه، {len(test_matches)} بازی تست می‌شود.\n" + "="*60)

        # فاز دوم: شروع پیش‌بینی کورکورانه
        for index, match in enumerate(test_matches):
            fixture_id = match['fixture']['id']
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            match_date = match['fixture']['date'][:10]
            
            home_goals = match['goals']['home']
            away_goals = match['goals']['away']
            actual_result = f"{home_goals} - {away_goals}"

            print(f"\n[{index+1}/{len(test_matches)}] 🎯 تاریخ: {match_date} | {home_team} 🆚 {away_team}")

            # دریافت دیتای Predictions از ماشین
            pred_response = requests.get(f"{BASE_URL}/predictions", headers=HEADERS_SPORTS, params={"fixture": fixture_id})
            pred_data = pred_response.json().get("response", [])
            
            stats_text = "دیتای آماری در دسترس نیست."
            if pred_data:
                percent = pred_data[0].get('predictions', {}).get('percent', {})
                stats_text = f"شانس ماشین: برد میزبان {percent.get('home', 'N/A')} | مساوی {percent.get('draw', 'N/A')} | برد مهمان {percent.get('away', 'N/A')}"

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

            ai_prediction = predict_with_groq(mega_prompt)
            
            print(f"🤖 پیش‌بینی هوش مصنوعی: {ai_prediction.strip()}")
            print(f"📺 نتیجه واقعی در زمین:  {actual_result}")
            print("-" * 50)
            
            # ⚠️ ترمز اجباری ۶.۵ ثانیه‌ای برای جلوگیری از بلاک شدن توسط API-Sports و Groq
            time.sleep(6.5) 

        print("\n🏆 بک‌تست با موفقیت تمام شد! حالا درصد وین‌ریت را محاسبه کن.")

    except Exception as e:
        print(f"❌ خطا در اجرای اسکنر بهینه: {e}")

if __name__ == "__main__":
    run_optimized_backtest()
