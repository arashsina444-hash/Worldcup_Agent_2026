import os, requests, time
from datetime import datetime

API = os.environ.get("API_SPORTS_KEY")
GROQ = os.environ.get("GROQ_API_KEY")
HEADERS = {"x-apisports-key": API}

def append_to_log(log_text):
    # ذخیره پیش‌بینی‌ها در یک فایل برای محاسبه وین‌ریت در آینده
    with open("predictions_log.txt", "a", encoding="utf-8") as f:
        f.write(log_text + "\n")

def run_continuous_test():
    print("🚀 استارت موتور پیش‌بینی با حافظه دائم...")
    
    res = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"next": 5}).json()
    matches = res.get("response", [])
    
    if not matches:
        print("❌ خطای سرور در دریافت بازی‌ها.")
        return

    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    append_to_log(f"--- لاگ پیش‌بینی: {today_str} ---")

    for i, m in enumerate(matches):
        h, a = m['teams']['home']['name'], m['teams']['away']['name']
        fix_id = m['fixture']['id']
        date = m['fixture']['date'][:10]
        
        p_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json()
        stats = "دیتای خام"
        if p_res and p_res.get("response"):
            p = p_res["response"][0].get("predictions", {}).get("percent", {})
            stats = f"برد {p.get('home', '')} | مساوی {p.get('draw', '')} | برد مهمان {p.get('away', '')}"
        
        prompt = f"بازی {h} 🆚 {a}. آمار: {stats}. تو تحلیلگر جسوری هستی. فقط نتیجه نهایی (مثل 2-1) را پیش‌بینی کن. کلمه اضافه‌ای ننویس."
        
        try:
            groq = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {GROQ}"}, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7})
            ai = groq.json()['choices'][0]['message']['content'].strip()
        except:
            ai = "خطا"
            
        result_str = f"[{date}] {h} 🆚 {a} | پیش‌بینی ماشین: {ai}"
        print(f"[{i+1}/5] {result_str}")
        
        # ثبت در حافظه برای محاسبه وین‌ریت
        append_to_log(result_str)
        time.sleep(6)

if __name__ == "__main__": 
    run_continuous_test()
