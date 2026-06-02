import os
import requests
import time

API_SPORTS_KEY = os.environ.get("API_SPORTS_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
HEADERS_SPORTS = {"x-apisports-key": API_SPORTS_KEY}
BASE_URL = "https://v3.football.api-sports.io"

def predict_with_groq(mega_prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": mega_prompt}], "temperature": 0.7}
    try:
        return requests.post(url, headers=headers, json=data).json()['choices'][0]['message']['content']
    except:
        return "❌ خطای گروق"

def run_micro_backtest():
    print("⏳ در حال دریافت ۱۰ بازی آخر لیگ برتر انگلیس...")
    
    # فقط ۱ ریکوئست برای گرفتن ۱۰ بازی آخر! (بدون هیچ فیلتر پیچیده‌ای)
    response = requests.get(f"{BASE_URL}/fixtures", headers=HEADERS_SPORTS, params={"league": 39, "season": 2025, "last": 10})
    matches = response.json().get("response", [])
    
    for index, match in enumerate(matches):
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        actual_result = f"{match['goals']['home']} - {match['goals']['away']}"
        
        # دریافت دیتای Prediction
        pred_response = requests.get(f"{BASE_URL}/predictions", headers=HEADERS_SPORTS, params={"fixture": match['fixture']['id']})
        pred_data = pred_response.json().get("response", [])
        
        stats = "نامشخص"
        if pred_data:
            p = pred_data[0].get('predictions', {}).get('percent', {})
            stats = f"برد میزبان {p.get('home', '')} | مساوی {p.get('draw', '')} | برد مهمان {p.get('away', '')}"
        
        prompt = f"بازی: {home} 🆚 {away}. آمار ماشین: {stats}. با در نظر گرفتن مزیت میزبانی محتاطانه و جسارت در مساوی، فقط و فقط نتیجه نهایی (مثل ۱-۱) را پیش‌بینی کن. هیچ کلمه اضافه‌ای ننویس."
        
        ai_pred = predict_with_groq(prompt)
        print(f"[{index+1}/10] {home} 🆚 {away} | 🤖 پیش‌بینی: {ai_pred.strip()} | 📺 نتیجه واقعی: {actual_result}")
        
        time.sleep(3) # ترمز امنیتی

if __name__ == "__main__":
    run_micro_backtest()
