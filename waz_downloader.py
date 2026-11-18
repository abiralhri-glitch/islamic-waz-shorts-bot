"""
Islamic Waz Short Reels Downloader & YouTube/TikTok Multi-Source Engine
- STRICT POLICY: ZERO Facebook URLs (100% YouTube Shorts & TikTok Only)
- STRICT POLICY: 100% Natural Original Audio (NO Chipmunk / NO Pitch Shifting)
- STRICT POLICY: Zero Duplicate System (Facebook Graph API + History Verification)
"""

import os
import re
import sys
import json
import random
import logging
import subprocess
import requests
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "posted_waz_history.json")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Curated Authentic YouTube Shorts Collection (100% Real Live Speaker Footage)
CURATED_YOUTUBE_SHORTS = [
    # মিজানুর রহমান আজহারী
    {
        "scholar": "মিজানুর রহমান আজহারী",
        "title": "মিজানুর রহমান আজহারী: জীবনের শ্রেষ্ঠ নসিহত ও সময়ের মূল্যায়ন",
        "url": "https://www.youtube.com/shorts/3nYHjmjFpYQ",
        "src_id": "yt_3nYHjmjFpYQ",
        "nasihat": "প্রতিটি নিঃশ্বাস এক একটি মূল্যবান নেয়ামত। দুনিয়ার মোহে পড়ে আখিরাত ভুলে যাবেন না।",
        "hashtags": "#MizanurRahmanAzhari #AzhariWaz #IslamicReminder #WazShorts #BanglaWaz"
    },
    {
        "scholar": "মিজানুর রহমান আজহারী",
        "title": "মিজানুর রহমান আজহারী: হৃদয়স্পর্শী নসিহত ও আমলের গুরুত্ব",
        "url": "https://www.youtube.com/shorts/6r9r87KxPPM",
        "src_id": "yt_6r9r87KxPPM",
        "nasihat": "এমন কিছু নেক আমল রেখে যান যা কবরে আপনার আলোর কারণ হবে।",
        "hashtags": "#MizanurRahmanAzhari #AzhariShorts #IslamicBayan #HeartTouching"
    },
    {
        "scholar": "মিজানুর রহমান আজহারী",
        "title": "মিজানুর রহমান আজহারী: পিতামাতার মর্যাদা ও তাদের প্রতি আচরণ",
        "url": "https://www.youtube.com/shorts/cgiYvYaIFG8",
        "src_id": "yt_cgiYvYaIFG8",
        "nasihat": "পিতামাতার সন্তুষ্টিতেই মহান আল্লাহর সন্তুষ্টি নিহিত। তাদের খেদমত করুন।",
        "hashtags": "#ParentsInIslam #AzhariWaz #IslamicFamily #MizanurRahmanAzhari"
    },
    {
        "scholar": "মিজানুর রহমান আজহারী",
        "title": "মিজানুর রহমান আজহারী: আল্লাহর অসীম রহমত ও খাঁটি তওবা",
        "url": "https://www.youtube.com/shorts/RYR9LJ-noiU",
        "src_id": "yt_RYR9LJ-noiU",
        "nasihat": "পাপ যত বড়ই হোক, আল্লাহর রহমত তার চেয়েও অনেক বড়। খাঁটি তওবা করুন।",
        "hashtags": "#Tawbah #AllahMercy #AzhariBayan #Sunnah"
    },
    # আবু ত্বহা মোহাম্মদ আদনান
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: টেনশন করো না, আল্লাহ সাথে আছেন",
        "url": "https://www.youtube.com/shorts/FMwP2Nq78Jg",
        "src_id": "yt_FMwP2Nq78Jg",
        "nasihat": "বিপদাপদে আল্লাহর ওপর পূর্ণ তাওয়াক্কুল রাখুন, নিশ্চয়ই তিনি ধৈর্যশীলদের সাথে আছেন।",
        "hashtags": "#AbuTohaAdnan #AbuTohaWaz #Tawakkul #PeaceOfMind"
    },
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: আখিরাতের প্রস্তুতি ও শেষ জামানা",
        "url": "https://www.youtube.com/shorts/7tOiZnzuh84",
        "src_id": "yt_7tOiZnzuh84",
        "nasihat": "সকাল ও সন্ধ্যার মাসনুন দোয়া এবং সূরা আল-কাহাফ নিয়মিত তিলাওয়াত করুন।",
        "hashtags": "#AbuTohaAdnan #SheshJamana #Eman #IslamicReels"
    },
    # শায়খ আহমাদুল্লাহ
    {
        "scholar": "শায়খ আহমাদুল্লাহ",
        "title": "শায়খ আহমাদুল্লাহ: দোয়ার ফজিলত ও কবুলের গোপন রহস্য",
        "url": "https://www.youtube.com/shorts/yXH8rPQ3l2M",
        "src_id": "yt_yXH8rPQ3l2M",
        "nasihat": "তাহাজ্জুদের সময় ও সেজদায় গিয়ে রবের কাছে আকুল হয়ে চান, দোয়া ফিরিয়ে দেওয়া হয় না।",
        "hashtags": "#ShaykhAhmadullah #AhmadullahWaz #Dua #Sunnah"
    },
    {
        "scholar": "শায়খ আহমাদুল্লাহ",
        "title": "শায়খ আহমাদুল্লাহ: উত্তম চরিত্র ও সুন্দর পারিবারিক জীবন",
        "url": "https://www.youtube.com/shorts/y31MzRdIDPo",
        "src_id": "yt_y31MzRdIDPo",
        "nasihat": "রাসুলুল্লাহ (সা.) বলেছেন: তোমাদের মধ্যে সর্বোত্তম ব্যক্তি সে, যে পরিবারের কাছে উত্তম।",
        "hashtags": "#ShaykhAhmadullah #FamilyLife #Akhlaq #IslamicReminder"
    },
    # আল্লামা দেলাওয়ার হোসাইন সাঈদী
    {
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "title": "আল্লামা দেলাওয়ার হোসাইন সাঈদী: কোরআনের আলো ও হেদায়েতের ডাক",
        "url": "https://www.youtube.com/shorts/QV8QDT5S4Qg",
        "src_id": "yt_QV8QDT5S4Qg",
        "nasihat": "কোরআনের ছায়াতলে ফিরে আসুন, সেখানেই রয়েছে দুনিয়া ও আখিরাতের চূড়ান্ত মুক্তি।",
        "hashtags": "#DelowarHossainSayedi #AllamaSayedi #SayediWaz #QuranerDawat"
    },
    {
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "title": "আল্লামা দেলাওয়ার হোসাইন সাঈদী: কালজয়ী আবেগঘন শ্রেষ্ঠ নসিহত",
        "url": "https://www.youtube.com/shorts/u92CrHYHka4",
        "src_id": "yt_u92CrHYHka4",
        "nasihat": "নিশ্চয়ই মহান আল্লাহ তওবাকারীদের অত্যন্ত ভালোবাসেন। বিলম্ব না করে ফিরে আসুন।",
        "hashtags": "#AllamaSayedi #SayediShorts #HeartTouching #Tawbah"
    }
]

# Dynamic Search Queries for Fresh Shorts on YouTube & TikTok
DYNAMIC_SCHOLAR_QUERIES = [
    ("মিজানুর রহমান আজহারী", "মিজানুর রহমান আজহারী shorts #shorts", "#MizanurRahmanAzhari #AzhariWaz"),
    ("আবু ত্বহা মোহাম্মদ আদনান", "আবু ত্বহা আদনান shorts #shorts", "#AbuTohaAdnan #AbuTohaWaz"),
    ("শায়খ আহমাদুল্লাহ", "শায়খ আহমাদুল্লাহ shorts #shorts", "#ShaykhAhmadullah #AhmadullahWaz"),
    ("আল্লামা দেলাওয়ার হোসাইন সাঈদী", "আল্লামা সাঈদী shorts #shorts", "#AllamaSayedi #SayediWaz"),
    ("মাওলানা তারেক জামিল", "মাওলানা তারেক জামিল বাংলা shorts #shorts", "#MaulanaTariqJamil #TariqJamilBangla")
]

def get_posted_signatures_from_facebook(page_id: str, access_token: str, limit: int = 100) -> set:
    """ফেসবুক পেজ থেকে সরাসরি পূর্বে পোস্ট করা সকল ভিডিওর সিগনেচার ও সোর্স আইডি রিটার্ন করে"""
    signatures = set()
    if not access_token or not page_id:
        return signatures
    try:
        url = f"https://graph.facebook.com/v21.0/{page_id}/videos"
        res = requests.get(url, params={"access_token": access_token, "fields": "description,title", "limit": limit}, timeout=15).json()
        for v in res.get("data", []):
            desc = v.get("description", "")
            title = v.get("title", "")
            m = re.search(r"\[src:([a-zA-Z0-9_.-]+)\]", desc)
            if m:
                signatures.add(m.group(1))
            if title:
                signatures.add(title.strip()[:40])
            first_line = desc.strip().split("\n")[0]
            if first_line:
                signatures.add(first_line.strip()[:40])
    except Exception as e:
        logging.warning(f"Failed to fetch Facebook video signatures: {e}")
    return signatures

def load_local_history() -> set:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data) if isinstance(data, list) else set(data.get("posted_ids", []))
        except Exception:
            return set()
    return set()

def save_local_history(new_id: str):
    history = list(load_local_history())
    if new_id not in history:
        history.append(new_id)
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.warning(f"Failed to save local history: {e}")

def download_youtube_short(video_url: str, output_path: str, max_duration: int = 90) -> bool:
    """YouTube Shorts / TikTok থেকে ভিডিও ডাউনলোড করে (নো ফেসবুক)"""
    logging.info(f"Downloading short from: {video_url}")
    cmd = [
        "yt-dlp",
        video_url,
        "-f", "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--match-filter", f"duration <= {max_duration} & duration >= 15",
        "--no-playlist",
        "-o", output_path,
        "--max-downloads", "1"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if (res.returncode in (0, 101)) and os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            logging.info(f"Downloaded short successfully: {output_path} ({os.path.getsize(output_path)} bytes)")
            return True
        logging.warning(f"yt-dlp download failed. rc={res.returncode}, stderr={res.stderr[-300:]}")
    except Exception as e:
        logging.warning(f"yt-dlp execution error: {e}")
    return False

def search_dynamic_youtube_short(query: str, exclude_signatures: set, output_path: str) -> dict:
    """YouTube এ সার্চ করে সম্পূর্ণ নতুন ও অপ্রকাশিত ভিডিও ডাউনলোড করে"""
    logging.info(f"Searching YouTube for fresh shorts: '{query}'")
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-warnings",
        f"ytsearch8:{query}"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        for line in res.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                info = json.loads(line)
                vid = info.get("id")
                dur = info.get("duration") or 0
                title = info.get("title", "")
                src_id = f"yt_{vid}"

                if dur < 15 or dur > 90:
                    continue
                if src_id in exclude_signatures or title[:40] in exclude_signatures:
                    logging.info(f"Skipping already posted video: {src_id} | {title[:30]}")
                    continue

                # Unposted fresh video found! Download it
                watch_url = f"https://www.youtube.com/shorts/{vid}"
                if download_youtube_short(watch_url, output_path, max_duration=90):
                    return {
                        "src_id": src_id,
                        "title": title,
                        "url": watch_url,
                        "duration": dur
                    }
            except Exception:
                continue
    except Exception as e:
        logging.warning(f"Dynamic YouTube search error: {e}")
    return {}
