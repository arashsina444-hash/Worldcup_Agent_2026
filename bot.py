import os, requests
import json

API = os.environ.get("API_SPORTS_KEY")
HEADERS = {"x-apisports-key": API}
BASE_URL = "https://v3.football.api-sports.io/fixtures"

def run_truth_serum():
    print("🔍 در حال تزریق سرم حقیقت به سرور API-Sports...\n")
    
    # تست ۱: آیا مشکل از نذاشتن فصل (Season) است؟
    print("--- تست ۱: درخواست بازی‌های لیگ ۳۹ بدون ذکر فصل ---")
    res1 = requests.get(BASE_URL, headers=HEADERS, params={"league": 39, "last": 2}).json()
    print(json.dumps(res1, indent=2, ensure_ascii=False))
    
    # تست ۲: آیا مشکل از عدد ۲۰۲۵ است؟
    print("\n--- تست ۲: درخواست با فصل ۲۰۲۵ ---")
    res2 = requests.get(BASE_URL, headers=HEADERS, params={"league": 39, "season": 2025, "last": 2}).json()
    print(json.dumps(res2, indent=2, ensure_ascii=False))

    # تست ۳: نکند API تقویمش را آپدیت کرده و الان فصل ۲۰۲۶ است؟!
    print("\n--- تست ۳: درخواست با فصل ۲۰۲۶ ---")
    res3 = requests.get(BASE_URL, headers=HEADERS, params={"league": 39, "season": 2026, "last": 2}).json()
    print(json.dumps(res3, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run_truth_serum()
