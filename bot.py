import os
import requests

API_SPORTS_KEY = os.environ.get("API_SPORTS_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS_SPORTS = {"x-apisports-key": API_SPORTS_KEY}

def check_api_status():
    print("🩺 در حال اسکن وضعیت اکانت API-Sports شما...")
    try:
        response = requests.get(f"{BASE_URL}/status", headers=HEADERS_SPORTS)
        data = response.json()
        
        # بررسی ارورهای پنهان
        errors = data.get("errors", [])
        if errors:
            print(f"❌ ارور از سمت سرور API: {errors}")
            
        account_info = data.get("response", {})
        if account_info:
            subscription = account_info.get("subscription", {})
            requests_info = account_info.get("requests", {})
            
            print("\n📊 وضعیت اکانت شما:")
            print(f"🔹 نوع اشتراک: {subscription.get('plan', 'نامشخص')}")
            
            print("\n🔋 وضعیت مصرفِ امروز (سهمیه ۱۰۰ تایی):")
            print(f"🔸 تعداد مجاز امروز: {requests_info.get('limit_day', 0)}")
            print(f"🔸 مصرف شده تا این لحظه: {requests_info.get('current', 0)}")
            
            if int(requests_info.get('current', 0)) >= int(requests_info.get('limit_day', 0)):
                print("\n🚨 اخطار قرمز: سهمیه ۱۰۰ درخواست شما برای امروز کاملاً تمام شده است!")
                print("💡 راه‌حل ۱: باید تا نیمه‌شب (ریست شدن تایمر سرور) صبر کنید.")
                print("💡 راه‌حل ۲: با یک ایمیل جدید در سایت API-Football ثبت‌نام کنید و کلید جدید را در بخش Secrets گیت‌هاب جایگزین کنید.")
            else:
                print("\n✅ شما هنوز سهمیه دارید. پس مشکل از جای دیگری است (که بعید می‌دانم).")

    except Exception as e:
        print(f"❌ خطای ارتباطی: {e}")

if __name__ == "__main__":
    check_api_status()
