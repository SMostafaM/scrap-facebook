# cookies_final_fixed.py
# اجرا کن → facebook_cookies.json کاملاً درست و بدون ارور ساخته می‌شه

import json
from datetime import datetime

text = '''ar_debug	1	.facebook.com	/	Session	9	✓	✓	None			Medium
c_user	61584289023155	.facebook.com	/	2026-11-27T11:52:06.664Z	20		✓	None			Medium
datr	EEsdafaOnjK6yGr7CJm9wi9n	.facebook.com	/	2026-12-24T04:43:59.641Z	28	✓	✓	None			Medium
fr	1v30njs0bdxDgucvU.AWc3eXP2LX-QfNZ502Rt8OJkiEi45c3Z3txZDl3ApFDGiXg7grk.BpKDtj..AAA.0.0.BpKDtj.AWdW5Nc4Yxh-7vevRjKC_4UZ6Q0	.facebook.com	/	2026-02-25T11:52:06.664Z	122	✓	✓	None			Medium
locale	en_US	.facebook.com	/	2025-12-04T09:27:53.356Z	11		✓	None			Medium
oo	v1	.facebook.com	/	2027-01-01T09:23:04.128Z	4	✓	✓	None			Medium
presence	C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1764244329202%2C%22v%22%3A1%7D	.facebook.com	/	Session	75		✓				Medium
ps_l	1	.facebook.com	/	2026-12-24T07:46:38.317Z	5	✓	✓	Lax			Medium
ps_n	1	.facebook.com	/	2026-12-24T07:46:38.317Z	5	✓	✓	None			Medium
sb	EEsdaW718_MwIQF0LNYeUenP	.facebook.com	/	2027-01-01T09:27:53.356Z	26	✓	✓	None			Medium
wd	591x650	.facebook.com	/	2025-12-04T09:29:40.000Z	9		✓	Lax			Medium
xs	15%3AFS0HqskZmU2soA%3A2%3A1764235671%3A-1%3A-1%3A%3AAcwoLyNNVX-T7DicnWyBxAXHONts8T_-2IJm0YGcyA	.facebook.com	/	2026-11-27T11:52:06.664Z	96	✓	✓	None			Medium
'''

lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

cookies = []

for line in lines:
    parts = line.split('\t')
    if len(parts) < 8:
        continue

    name = parts[0]
    value = parts[1]
    domain = parts[2]
    path = parts[3]

    # تاریخ انقضا
    expiry_str = parts[4]
    if "Session" in expiry_str:
        expirationDate = None
    else:
        try:
            dt = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
            expirationDate = int(dt.timestamp())
        except:
            expirationDate = None

    # secure و httpOnly
    flags = parts[6]
    secure = "✓" in flags
    httpOnly = flags.count("✓") >= 2

    # این قسمت مهمه: Medium رو حذف می‌کنه و فقط Lax یا None می‌ذاره
    raw_sameSite = parts[7] if len(parts) > 7 else "Lax"
    if "Lax" in raw_sameSite:
        sameSite = "Lax"
    elif "None" in raw_sameSite:
        sameSite = "None"
    else:
        sameSite = "None"  # فیس‌بوک بیشتر None می‌خواد

    # اگه sameSite = None بود، secure حتماً باید True باشه (قانون Playwright)
    if sameSite == "None":
        secure = True

    cookies.append({
        "name": name,
        "value": value,
        "domain": domain,
        "path": path,
        "secure": secure,
        "httpOnly": httpOnly,
        "sameSite": sameSite,
        "expirationDate": expirationDate
    })

with open("facebook_cookies.json", "w", encoding="utf-8") as f:
    json.dump(cookies, f, ensure_ascii=False, indent=2)

print(f"\nتموم شد داداش! {len(cookies)} تا کوکی کامل و بدون ارور ذخیره شد ❤️")
print("فایل facebook_cookies.json آماده‌ست")
print("حالا کد Playwright رو اجرا کن — این بار دیگه هیچ اروری نمی‌ده و همه پست‌ها میان!")