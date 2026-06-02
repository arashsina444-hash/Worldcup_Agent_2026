import os, requests, time

API, GROQ = os.environ.get("API_SPORTS_KEY"), os.environ.get("GROQ_API_KEY")
HEADERS = {"x-apisports-key": API}

def run_bulletproof_test():
    print("⏳ در حال دریافت ۱۵ بازی آخرِ تمام‌شده (مسیرِ میان‌بر بدون تاریخ)...")
    
    # فقط یک درخواست ساده و بی‌رحمانه: آخرین بازی‌های لیگ انگلیس که تمام شده‌اند
    res = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"league": 39, "status": "FT", "last": 15}).json()
    
    matches = res.get("response", [])
    if not matches:
        print("❌ خطای سرور. لیستی دریافت نشد.")
        return

    for i, m in enumerate(matches):
        h, a = m['teams']['home']['name'], m['teams']['away']['name']
        actual = f"{m['goals']['home']} - {m['goals']['away']}"
        
        # دریافت آمار پیشرفته
        p_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": m['fixture']['id']}).json()
        stats = "دیتای خام"
        if p_res and p_res.get("response"):
            p = p_res["response"][0].get("predictions", {}).get("percent", {})
            stats = f"برد میزبان {p.get('home', '')} | مساوی {p.get('draw', '')} | برد مهمان {p.get('away', '')}"
        
        # پرامپت نقطه‌زن
        prompt = f"بازی {h} 🆚 {a}. آمار: {stats}. تو یک تحلیلگر جسور هستی. فقط نتیجه نهایی فوتبال را پیش‌بینی کن (مثل 2-1). هیچ کلمه‌ای اضافه‌تر ننویس."
        
        groq = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {GROQ}"}, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7})
        
        try:
            ai = groq.json()['choices'][0]['message']['content'].strip()
        except:
            ai = "خطای هوش مصنوعی"
            
        print(f"[{i+1}/15] {h} 🆚 {a} | 🤖 پیش‌بینی ماشین: {ai} | 📺 واقعیت: {actual}")
        time.sleep(5) # ترمز امنیتی

if __name__ == "__main__": 
    run_bulletproof_test()
