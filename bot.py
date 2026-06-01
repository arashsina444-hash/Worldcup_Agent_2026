import os
import requests
import json
from datetime import datetime

# ۱. فراخوانی امنِ کلید از متغیرهای محیطی (Environment Variables / GitHub Secrets)
API_KEY = os.environ.get("API_SPORTS_KEY")

if not API_KEY:
    print("❌ خطا: متغیر 'API_SPORTS_KEY' پیدا نشد! اگر روی سیستم محلی هستی، آن را تنظیم کن.")
    exit()

BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

def get_todays_fixtures():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"🔄 در حال اتصال به سرور مرکزی برای بازی‌های امروز ({today})...")
    
    url = f"{BASE_URL}/fixtures"
    querystring = {"date": today}
    
    try:
        response = requests.get(url, headers=HEADERS, params=querystring)
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data and data["errors"]:
            print(f"❌ خطای سرور API: {data['errors']}")
            return

        matches = data.get("response", [])
        
        if not matches:
            print("📭 امروز هیچ بازی مهمی در دیتابیس یافت نشد.")
            return
            
        print(f"✅ تعداد {len(matches)} بازی دریافت شد. (نمایش ۵ بازی اول):\n")
        print("-" * 40)
        
        for match in matches[:5]:
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            league = match['league']['name']
            status = match['fixture']['status']['long']
            
            print(f"🏆 لیگ: {league}")
            print(f"⚽ مسابقه: {home_team} 🆚 {away_team}")
            print(f"وضعیت: {status}")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ خطا در ارتباط با سرور: {e}")

if __name__ == "__main__":
    get_todays_fixtures()
