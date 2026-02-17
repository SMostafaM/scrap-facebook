# FINAL_بدون_هیچ_خطایی_و_همه_چیز_میاره.py
# متن + عکس + ویدیو + دانلود فوری + Enter = توقف

import threading
import os
import requests
import json
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

TARGET_PROFILE = "https://www.facebook.com/profile.php?id=61557462146785"
COOKIES_FILE = "/Users/smostafa/Desktop/Project/facebook_collect/collect post/facebook_cookies.json"
DOWNLOAD_FOLDER = "/Users/smostafa/Desktop/post_5_1"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

final_posts = []
downloaded_count = 0
stop_requested = False

def download_file(url, folder):
    global downloaded_count
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, stream=True, timeout=60)
        if r.status_code == 200:
            ext = ".jpg"
            if "video" in r.headers.get("content-type", "") or ".mp4" in url: ext = ".mp4"
            elif ".png" in url: ext = ".png"
            filename = f"{datetime.now().strftime('%Y-%m-%d')}_{downloaded_count:04d}{ext}"
            filepath = os.path.join(folder, filename)
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(1024*1024):
                    f.write(chunk)
            downloaded_count += 1
            print(f"دانلود شد → {filename}")
            return filename
    except: pass
    return None

def input_listener():
    global stop_requested
    input("\nهر وقت خواستی تموم بشه → Enter بزن...\n")
    stop_requested = True
    print("در حال توقف و ذخیره نهایی...")

threading.Thread(target=input_listener, daemon=True).start()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=250)
    context = browser.new_context()
    
    with open(COOKIES_FILE, encoding="utf-8") as f:
        cookies = json.load(f)
    context.add_cookies(cookies)
    
    page = context.new_page()

    # ضد تایم‌اوت
    for _ in range(5):
        try:
            page.goto(TARGET_PROFILE, wait_until="domcontentloaded", timeout=90000)
            time.sleep(10)
            break
        except:
            time.sleep(10)
    else:
        print("نشد؟ یه بار دستی وارد شو بعد دوباره کد رو بزن")
        input(); browser.close(); exit()

    print("شروع اسکرول — همه چیز رو می‌گیرم\n")
    last_height = 0

    while not stop_requested:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(random.uniform(3, 7))

        posts = page.query_selector_all("div[role='article']")
        
        for post in posts:
            item = {"date": "نامشخص", "text": "", "files": [], "urls": []}

            # تاریخ
            try:
                date_el = post.query_selector("a[href*='/posts/'] span span, a[href*='/photos/'] span span")
                if date_el: item["date"] = date_el.inner_text().strip()
            except: pass

            # متن
            try:
                text_el = post.query_selector("div[data-ad-preview='message']")
                if text_el: item["text"] = text_el.inner_text().strip()
            except: pass

            # عکس و ویدیو — درست شده!
            for elem in post.query_selector_all("img, video"):
                # درست گرفتن تگ
                tag = elem.evaluate("el => el.tagName", elem).lower()

                src = None
                if tag == "img":
                    srcset = elem.get_attribute("srcset")
                    if srcset:
                        urls = [u.strip().split(" ")[0] for u in srcset.split(",") if u.strip()]
                        src = urls[-1] if urls else None
                    if not src:
                        src = elem.get_attribute("src")
                elif tag == "video":
                    src = elem.get_attribute("src")
                    if not src:
                        source = elem.query_selector("source")
                        if source: src = source.get_attribute("src")

                if src and src.startswith("https://") and ("fbcdn" in src or "scontent" in src):
                    if any(bad in src for bad in ["72x", "130x", "96x", "emoji", "profile", "static.xx.fbcdn.net/images/emoji"]):
                        continue
                    if src not in item["urls"]:
                        item["urls"].append(src)
                        fn = download_file(src, DOWNLOAD_FOLDER)
                        if fn: item["files"].append(fn)

            if item["text"] or item["files"]:
                if not any(p.get("text") == item["text"] and p.get("date") == item["date"] for p in final_posts):
                    final_posts.append(item)
                    print(f"پست جدید: {item['date']} | {len(item['files'])} فایل")

        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(20)
            if new_height == page.evaluate("document.body.scrollHeight"):
                break
        last_height = new_height

    browser.close()

# ذخیره نهایی
json_path = os.path.join(DOWNLOAD_FOLDER, "خاطرات_کامل.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(final_posts, f, ensure_ascii=False, indent=2)

print(f"\nتموم شد داداش!")
print(f"تعداد پست: {len(final_posts)} تا")
print(f"تعداد فایل دانلود شده: {downloaded_count} تا")
print(f"همه چیز تو: {DOWNLOAD_FOLDER}")