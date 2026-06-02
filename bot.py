import os, requests, time

API = os.environ.get("API_SPORTS_KEY")
GROQ = os.environ.get("GROQ_API_KEY")
HEADERS = {"x-apisports-key": API}

def run_future_test():
    print("🚀 در حال استخراج ۵ مسابقه آینده در جهان (تست زنده)...")
    
    # پارامتر next: گرفتن بازی‌های آینده بدون درگیر شدن با فصل و تاریخ
    res = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"next": 5}).json()
    matches = res.get("response", [])
    
    if not matches:
        print("❌ خطای سرور یا اتمام سهمیه.")
        return

    for i, m in enumerate(matches):
        h, a = m['teams']['home']['name'], m['teams']['away']['name']
        fix_id = m['fixture']['id']
        date = m['fixture']['date'][:10]
        
        p_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json()
        stats = "دیتای خام"
        if p_res and p_res.get("response"):
            p = p_res["response"][0].get("predictions", {}).get("percent", {})
            stats = f"برد میزبان {p.get('home', '')} | مساوی {p.get('draw', '')} | برد مهمان {p.get('away', '')}"
        
        prompt = f"بازی {h} 🆚 {a}. آمار ماشین: {stats}. تو یک تحلیلگر جسور هستی. فقط نتیجه نهایی فوتبال را پیش‌بینی کن (مثل 2-1). کلمه اضافه‌ای ننویس."
        
        try:
            groq = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {GROQ}"}, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7})
            ai = groq.json()['choices'][0]['message']['content'].strip()
        except:
            ai = "خطای هوش مصنوعی"
            
        print(f"[{i+1}/5] تاریخ بازی: {date} | {h} 🆚 {a} | 🤖 پیش‌بینی سوپراپ: {ai}")
        time.sleep(6) # ترمز امنیتی

if __name__ == "__main__": 
    run_future_test()
