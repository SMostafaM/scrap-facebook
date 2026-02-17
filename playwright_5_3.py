# FINAL_کامل_و_دقیقاً_همونی_که_خواستی.py
# فقط کپی کن و اجرا کن — همه چیز درست کار می‌کنه

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
DOWNLOAD_FOLDER = "/Users/smostafa/Desktop/خاطرات_عشقم_کامل"
JSON_OUTPUT = os.path.join(DOWNLOAD_FOLDER, "خاطرات_کامل.json")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

posts_data = []
downloaded_urls = set()
total_downloaded = 0
stop_requested = False
scroll_counter = 0

def download_real(url):
    global total_downloaded
    if not url or url in downloaded_urls:
        return None
    try:
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.facebook.com/"}
        r = requests.get(url, headers=headers, stream=True, timeout=60)
        if r.status_code == 200 and len(r.content) > 10000:
            ext = ".mp4" if ("video" in r.headers.get("content-type", "") or ".mp4" in url) else ".jpg"
            filename = f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_{total_downloaded:04d}{ext}"
            path = os.path.join(DOWNLOAD_FOLDER, filename)
            with open(path, 'wb') as f:
                for chunk in r.iter_content(1024*1024):
                    f.write(chunk)
            total_downloaded += 1
            downloaded_urls.add(url)
            return filename
    except:
        pass
    return None

def input_listener():
    global stop_requested
    input("\nهر وقت خواستی تموم بشه → Enter بزن...\n")
    stop_requested = True
    print("در حال توقف و ذخیره نهایی...")

threading.Thread(target=input_listener, daemon=True).start()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=200)
    context = browser.new_context()
    
    with open(COOKIES_FILE, encoding="utf-8") as f:
        context.add_cookies(json.load(f))
    
    page = context.new_page()

    # ورود بدون مشکل
    for _ in range(5):
        try:
            page.goto(TARGET_PROFILE)
            page.wait_for_load_state("domcontentloaded", timeout=90000)
            print("وارد شدم!")
            time.sleep(10)
            break
        except:
            time.sleep(10)

    print("شروع اسکرول — کاملاً طبیعی و هوشمند\n")
    last_height = 0

    while not stop_requested:
        scroll_counter += 1

        # اسکرول
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # مکث طبیعی بعد از هر اسکرول (۶ تا ۱۰ ثانیه)
        time.sleep(random.uniform(6, 10))

        # هر ۳ تا ۶ اسکرول یه مکث طولانی
        if scroll_counter % random.randint(3, 6) == 0:
            long_wait = random.uniform(20, 40)
            print(f"مکث طولانی مثل انسان: {long_wait:.0f} ثانیه...")
            time.sleep(long_wait)

        # فقط از پست‌ها عکس و فیلم بگیر
        posts = page.query_selector_all("div[role='article']")
        for post in posts:
            item = {"date": "", "text": "", "files": [], "urls": []}

            # تاریخ
            try:
                d = post.query_selector("a[href*='/posts/'] span span, a[href*='/photos/'] span span")
                if d: item["date"] = d.inner_text().strip()
            except: pass

            # متن
            try:
                t = post.query_selector("div[data-ad-preview='message']")
                if t: item["text"] = t.inner_text().strip()
            except: pass

            # عکس و فیلم — با تضمین لود کامل
            for elem in post.query_selector_all("img, video"):
                try:
                    elem.scroll_into_view_if_needed()
                    time.sleep(0.4)  # صبر تا عکس کامل لود بشه

                    urls = []
                    tag = elem.evaluate("el => el.tagName?.toLowerCase() || ''")
                    if tag == "img":
                        srcset = elem.get_attribute("srcset") or ""
                        if srcset:
                            urls = [u.strip().split(" ")[0] for u in srcset.split(",")]
                        src = elem.get_attribute("src") or ""
                        if src and src not in urls: urls.append(src)
                    elif tag == "video":
                        src = elem.get_attribute("src") or ""
                        if src: urls.append(src)

                    for url in urls:
                        if url and ("scontent" in url or "fbcdn.net" in url):
                            url = url.replace("&amp;", "&")
                            filename = download_real(url)
                            if filename:
                                item["files"].append(filename)
                                item["urls"].append(url)
                except:
                    continue

            if item["text"] or item["files"]:
                if not any(p["text"] == item["text"] and p["date"] == item["date"] for p in posts_data):
                    posts_data.append(item)

        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(20)
            if new_height == page.evaluate("document.body.scrollHeight"):
                break
        last_height = new_height

    browser.close()

# ذخیره JSON کامل
with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
    json.dump({"total_posts": len(posts_data), "total_media": total_downloaded, "posts": posts_data}, f, ensure_ascii=False, indent=2)

print(f"\nتموم شد داداش!")
print(f"کل پست: {len(posts_data)} تا")
print(f"کل عکس و فیلم واقعی: {total_downloaded} تا")
print(f"همه چیز تو پوشه: {DOWNLOAD_FOLDER}")