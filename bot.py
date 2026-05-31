import os
import requests
import json
from datetime import datetime

# تنظیمات پایه API (از API-Football در RapidAPI استفاده می‌کنیم)
API_KEY = "YOUR_RAPIDAPI_KEY_HERE"  # در مراحل بعدی کلید واقعی را اینجا می‌گذاریم
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

def fetch_upcoming_matches(date_str):
    """
    دریافت لیست بازی‌های یک تاریخ مشخص
    فرمت تاریخ باید YYYY-MM-DD باشد
    """
    print(f"در حال اتصال به دیتابیس جهانی برای تاریخ {date_str}...")
    url = f"{BASE_URL}/fixtures"
    querystring = {"date": date_str}
    
    try:
        # تا زمانی که کلید واقعی را نگرفته‌ایم، سیستم را هوشمندانه مدیریت می‌کنیم تا کرش نکند
        if API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
            print("⚠️ هشدار: کلید API هنوز تنظیم نشده است.")
            print("💡 برای دریافت کلید رایگان باید در سایت rapidapi.com ثبت‌نام کنیم.")
            return []
            
        response = requests.get(url, headers=HEADERS, params=querystring)
        response.raise_for_status()
        data = response.json()
        
        matches = data.get("response", [])
        print(f"✅ تعداد {len(matches)} بازی با موفقیت دریافت شد.")
        return matches
        
    except requests.exceptions.RequestException as e:
        print(f"❌ خطا در دریافت اطلاعات از سرور: {e}")
        return []

# بخش اجرایی اصلی سیستم (Entry Point)
if __name__ == "__main__":
    print("بستر ایجنت اوراکل فوتبال جام جهانی ۲۰۲۶ با موفقیت راه‌اندازی شد!")
    print("-" * 50)
    
    # تست دریافت بازی‌های امروز (۱ ژوئن ۲۰۲۶)
    today = datetime.now().strftime("%Y-%m-%d")
    matches_today = fetch_upcoming_matches(today)
