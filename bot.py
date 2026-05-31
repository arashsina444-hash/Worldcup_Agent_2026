import os
import requests
import json
from datetime import datetime

# تنظیمات پایه API 
API_KEY = "YOUR_RAPIDAPI_KEY_HERE"
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

def fetch_upcoming_matches(date_str):
    """
    دریافت لیست بازی‌های یک تاریخ مشخص
    """
    print(f"در حال اتصال به دیتابیس جهانی برای تاریخ {date_str}...")
    url = f"{BASE_URL}/fixtures"
    querystring = {"date": date_str}
    
    try:
        if API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
            print("⚠️ هشدار: کلید API هنوز تنظیم نشده است.")
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

def predict_match_result(home_team, away_team):
    """
    ماژول پیش‌بینی مبتنی بر احتمالات (نسخه MVP)
    """
    # این درصدها در آینده توسط دیتای واقعی جایگزین می‌شوند
    home_prob = 45
    draw_prob = 25
    away_prob = 30
    
    prediction_text = (
        f"📊 تحلیل احتمالات بازی: {home_team} مقابل {away_team}\n"
        f"🔹 شانس برد میزبان: {home_prob}%\n"
        f"🔹 شانس مساوی: {draw_prob}%\n"
        f"🔹 شانس برد میهمان: {away_prob}%\n"
        "💡 این یک پیش‌بینی اولیه است و به‌زودی با دیتای دقیق‌تر آپدیت می‌شود."
    )
    
    print(prediction_text)
    return prediction_text

def generate_daily_news():
    pass

def generate_historical_post():
    pass

if __name__ == "__main__":
    print("بستر ایجنت اوراکل فوتبال جام جهانی ۲۰۲۶ با موفقیت راه‌اندازی شد!")
    print("-" * 50)
    
    today = datetime.now().strftime("%Y-%m-%d")
    matches_today = fetch_upcoming_matches(today)
    
    print("-" * 50)
    # تست اولیه ماژول پیش‌بینی برای اطمینان از عملکرد
    predict_match_result("آرژانتین", "اسپانیا")
