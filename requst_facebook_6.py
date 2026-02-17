# FINAL_REQUESTS_WORKING_2025.py
# فقط اجرا کن — همه پست‌ها + عکس + ویدیو با کیفیت اصلی میاد

import requests
import json
import time

# اینا رو از پیامت کپی کردم
fb_dtsg = "NAfuZtQDGXk1vib2BUOU1BaSCkzEcfEZAR2ki_K2UBjIkHMSU68KNlw:26:1764091056"
c_user = "61584117413789"
xs = "26:uUaM4jpEOXjVMA:2:1764091056:-1:-1:AcxIMB6CSYoQ5b4BcmHezKqSnSYLVpQkv3xCfQZuKg"

# این doc_id جدیده که تو داشتی
doc_id = "25335766716116949"

# آیدی پروفایل
user_id = "61557462146785"

cookies = {
    "c_user": c_user,
    "xs": xs,
    "datr": "EEsdafaOnjK6yGr7CJm9wi9n",
    "sb": "EEsdaW718_MwIQF0LNYeUenP",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "X-FB-Friendly-Name": "ProfileCometTimelineFeedRefetchQuery",
    "Referer": f"https://www.facebook.com/profile.php?id={user_id}",
}

url = "https://www.facebook.com/api/graphql/"

variables = {
    "count": 30,
    "cursor": None,
    "scale": 1,
    "userID": user_id,
}

all_posts = []
cursor = None

print("شروع گرفتن همه پست‌ها — بدون اسکرول — مستقیم از فیس‌بوک\n")

while True:
    variables["cursor"] = cursor

    payload = {
        "av": c_user,
        "__user": c_user,
        "__a": "1",
        "fb_dtsg": fb_dtsg,
        "variables": json.dumps(variables),
        "doc_id": doc_id,
    }

    r = requests.post(url, headers=headers, cookies=cookies, data=payload)

    if r.status_code != 200:
        print("خطا:", r.status_code, r.text[:200])
        break

    data = r.json()

    edges = data["data"]["user"]["timeline_list_feed_units"]["edges"]

    for edge in edges:
        node = edge["node"]
        if "comet_sections" not in node:
            continue
        story = node["comet_sections"].get("content", {}).get("story", {})
        message = story.get("message", {}).get("text", "")
        attachments = story.get("attachments", [])

        images = []
        video = None

        for att in attachments:
            media = att.get("media", {})
            if media.get("__typename") == "Photo":
                img = media.get("image") or media.get("preview_image") or media.get("photo_image")
                if img and img.get("uri"):
                    images.append(img["uri"])
            elif media.get("__typename") == "Video":
                video = media.get("browser_native_hd_url") or media.get("browser_native_sd_url")

        if message or images or video:
            print(f"پست: {len(images)} عکس | ویدیو: {bool(video)} | {message[:60]}...")
            all_posts.append({"text": message, "images": images, "video": video})

    page_info = data["data"]["user"]["timeline_list_feed_units"]["page_info"]
    if not page_info.get("has_next_page"):
        break

    cursor = page_info["end_cursor"]
    time.sleep(2)

print(f"\nتموم شد! {len(all_posts)} تا پست گرفتم")
with open("خاطرات_واقعی_بدون_اسکرول.json", "w", encoding="utf-8") as f:
    json.dump(all_posts, f, ensure_ascii=False, indent=2)

print("فایل ذخیره شد: خاطرات_واقعی_بدون_اسکرول.json")