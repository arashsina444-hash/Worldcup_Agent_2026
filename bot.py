import os
import requests
import time

API_SPORTS_KEY = os.environ.get("API_SPORTS_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
HEADERS_SPORTS = {"x-apisports-key": API_SPORTS_KEY}
BASE_URL = "https://v3.football.api-sports.io"

TARGET_LEAGUES = [2, 39, 140, 135, 78, 61]
SEASON = 2025 # فصل فوتبالی که در ماه می ۲۰۲۶ به پایان می‌رسد

def predict_with_groq(mega_prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": mega_prompt}], "temperature": 0.7}
    try:
        return requests.post(url, headers=headers, json=data).json()['choices'][0]['message']['content']
    except:
        return "❌ خطای گروق"

def run_smart_backtest():
    print("⏳ موتور جستجوی هوشمند بازه‌ای روشن شد (May 2026)...")
    vip_matches = []
    
    # فاز اول: استخراج بهینه با ۶ ریکوئست
    for league_id in TARGET_LEAGUES:
        # کلید طلایی معماری جدید: استفاده از from و to
        response = requests.get(f"{BASE_URL}/fixtures", headers=HEADERS_SPORTS, params={
            "league": league_id, 
            "season": SEASON, 
            "from": "2026-05-01", 
            "to": "2026-05-31"
        })
        matches = response.json().get("response", [])
        for m in matches:
            if m['fixture']['status']['short'] in ['FT', 'PEN', 'AET']:
                vip_matches.append(m)
        
        time.sleep(1) # ترمز ۱ ثانیه‌ای کاملاً کافی است

    # مرتب‌سازی بر اساس تاریخ و محدود کردن به ۱۵ بازی برای حفظ سهمیه
    vip_matches.sort(key=lambda x: x['fixture']['date'])
    test_matches = vip_matches[:15]
    
    if not test_matches:
        print("📭 هیچ بازی در این بازه یافت نشد.")
        return

    print(f"✅ تعداد {len(test_matches)} بازی برای تست آماده شد.\n" + "="*50)

    # فاز دوم: بک‌تست
    for index, match in enumerate(test_matches):
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        actual = f"{match['goals']['home']} - {match['goals']['away']}"
        
        # دریافت دیتای Prediction
        pred_response = requests.get(f"{BASE_URL}/predictions", headers=HEADERS_SPORTS, params={"fixture": match['fixture']['id']})
        pred_data = pred_response.json().get("response", [])
        
        stats = "نامشخص"
        if pred_data:
            p = pred_data[0].get('predictions', {}).get('percent', {})
            stats = f"برد {p.get('home', '')} | مساوی {p.get('draw', '')} | برد مهمان {p.get('away', '')}"
        
        prompt = f"بازی: {home} 🆚 {away}. آمار ماشین: {stats}. با در نظر گرفتن مزیت میزبانی محتاطانه (۵۰ امتیاز) و جسارت در مساوی، فقط و فقط نتیجه نهایی (مثل ۱-۱) را پیش‌بینی کن. هیچ توضیح اضافه‌ای نده."
        
        ai_pred = predict_with_groq(prompt)
        print(f"[{index+1}] {home} 🆚 {away} | 🤖 پیش‌بینی: {ai_pred.strip()} | 📺 نتیجه واقعی: {actual}")
        
        time.sleep(6) # ترمز اجباری برای جلوگیری از ارور محدودیت سرعت سرورها

if __name__ == "__main__":
    run_smart_backtest()
