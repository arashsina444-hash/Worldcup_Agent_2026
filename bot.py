import os, requests, time

API = os.environ.get("API_SPORTS_KEY")
GROQ = os.environ.get("GROQ_API_KEY")
HEADERS = {"x-apisports-key": API}

def run_victory_test():
    print("🔥 شلیک نهایی به بازی‌های امروز (بدون هیچ فیلتر پولی و لیگی)...")
    
    # استفاده از تاریخ امروز که برای اکانت رایگان کاملاً باز است
    TODAY = "2026-06-02"
    res = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"date": TODAY}).json()
    
    if "errors" in res and res["errors"]:
        print("❌ ارور سرور:", res["errors"])
        return
        
    matches = res.get("response", [])
    if not matches:
        print("📭 واقعاً امروز هیچ بازی در دنیا برگزار نمی‌شود!")
        return

    print(f"✅ تعداد {len(matches)} بازی در دنیا پیدا شد. انتخاب ۲ بازی اول برای تست موتور هوش مصنوعی...\n" + "-"*40)
    
    for i, m in enumerate(matches[:2]):
        h, a = m['teams']['home']['name'], m['teams']['away']['name']
        fix_id = m['fixture']['id']
        
        # استخراج دیتای ماشین‌لرنینگ
        p_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json()
        stats = "دیتای خام در دسترس نیست"
        if p_res and p_res.get("response"):
            p = p_res["response"][0].get("predictions", {}).get("percent", {})
            stats = f"برد میزبان {p.get('home', '')} | مساوی {p.get('draw', '')} | برد مهمان {p.get('away', '')}"
        
        prompt = f"بازی {h} 🆚 {a}. آمار ماشین: {stats}. تو یک تحلیلگر جسور هستی. فقط نتیجه نهایی فوتبال را پیش‌بینی کن (مثل 2-1). کلمه اضافه‌ای ننویس."
        
        try:
            groq = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {GROQ}"}, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7})
            ai = groq.json()['choices'][0]['message']['content'].strip()
        except:
            ai = "خطای هوش مصنوعی"
            
        print(f"[{i+1}/2] {h} 🆚 {a} \n🤖 پیش‌بینی سوپراپ شما: {ai}\n")
        time.sleep(3)

if __name__ == "__main__": 
    run_victory_test()
