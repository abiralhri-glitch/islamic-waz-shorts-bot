"""
Islamic Waz Short Reels Downloader & Multi-Source Engine
- ১০০% আসল হুজুরদের লাইভ মাহফিল ও নসিহতের আসল সিনেমাটিক শর্ট ভিডিও
- সকল শীর্ষস্থানীয় সম্মানিত ইসলামিক স্কলারগণের অন্তর্ভুক্তিকরণ (আহমাদুল্লাহ, আজহারী, আবু ত্বহা, সাঈদী, আমির হামজা, তারেক জামিল)
- কঠোর জিরো-ডুপ্লিকেট পলিসি: ফেসবুক পেজের পূর্ববর্তী ১০০টি ভিডিওর মেটাডাটা ও হিস্টোরি যাচাই
- ১০০% স্বাভাবিক কণ্ঠস্বর: কোনো কার্টুন পিচ-শিফটিং বা ভয়েস স্পিড ডিস্টরশন নয়
- Resilient Android-Embedded Client to bypass YouTube bot detection on cloud runners
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

# অপরিবর্তনযোগ্য স্থায়ী ব্ল্যাকলিস্ট
PERMANENT_BANNED_SIGNATURES = {
    "bank_ahmadullah_life_advice",
    "bank_ahmadullah_dua",
    "ahmadullah_life_advice.mp4",
    "ahmadullah_dua.mp4",
    "yt_yXH8rPQ3l2M",
    "yt_y31MzRdIDPo",
    "জীনরা খাবার কোথায় পায়",
    "দোয়ার ফজিলত ও রবকে ডাকার গোপন রহস্য",
    "উত্তম চরিত্র ও সুন্দর পারিবারিক জীবনের শিক্ষা",
    "bank_amir_hamza_pother_alo",
    "amir_hamza_pother_alo.mp4",
    "4356847881114890",
    "bank_azhari_dile_shanti",
    "bank_abutoha_rizik_borot"
}

DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# সকল শীর্ষ সম্মানিত হুজুরদের ভেরিফাইড ট্রেন্ডিং ইউটিউব শর্টস কালেকশন
CURATED_YOUTUBE_SHORTS = [
    # ১. মাওলানা মিজানুর রহমান আজহারী
    {
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: জীবনের শ্রেষ্ঠ নসিহত ও সময়ের মূল্যায়ন",
        "url": "https://www.youtube.com/shorts/3nYHjmjFpYQ",
        "src_id": "yt_3nYHjmjFpYQ",
        "nasihat": "প্রতিটি নিঃশ্বাস এক একটি মূল্যবান নেয়ামত। দুনিয়ার মোহে পড়ে আখিরাত ভুলে যাবেন না।",
        "hashtags": "#MizanurRahmanAzhari #AzhariWaz #IslamicReminder #WazShorts #BanglaWaz"
    },
    {
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: পিতামাতার মর্যাদা ও তাদের প্রতি আচরণ",
        "url": "https://www.youtube.com/shorts/cgiYvYaIFG8",
        "src_id": "yt_cgiYvYaIFG8",
        "nasihat": "পিতামাতার সন্তুষ্টিতেই মহান আল্লাহর সন্তুষ্টি নিহিত। তাদের মন থেকে খেদমত করুন।",
        "hashtags": "#ParentsInIslam #AzhariWaz #IslamicFamily #MizanurRahmanAzhari"
    },
    {
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: আল্লাহর অসীম রহমত ও খাঁটি তওবা",
        "url": "https://www.youtube.com/shorts/C0bmgrBTEjM",
        "src_id": "yt_C0bmgrBTEjM",
        "nasihat": "পাপ যত বড়ই হোক, আল্লাহর রহমত তার চেয়েও অনেক বড়। খাঁটি অন্তরে তওবা করুন।",
        "hashtags": "#Tawbah #AllahMercy #AzhariBayan #Sunnah"
    },
    {
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: মানুষ চলে যায় কিন্তু নেক আমল রয়ে যায়",
        "url": "https://www.youtube.com/shorts/6r9r87KxPPM",
        "src_id": "yt_6r9r87KxPPM",
        "nasihat": "এমন কিছু নেক আমল রেখে যান যা কবরে আপনার আলোর কারণ হবে।",
        "hashtags": "#MizanurRahmanAzhari #AzhariShorts #IslamicBayan #HeartTouching"
    },
    {
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: হতাশ হবেন না, মহান রব আপনার সাথে আছেন",
        "url": "https://www.youtube.com/shorts/RYR9LJ-noiU",
        "src_id": "yt_RYR9LJ-noiU",
        "nasihat": "সব দরজা বন্ধ হয়ে গেলেও রবের রহমতের দরজা সর্বদা উন্মুক্ত। আল্লাহর ওপর ভরসা রাখুন।",
        "hashtags": "#MizanurRahmanAzhari #MotivationalWaz #Tawakkul #Peace"
    },

    # ২. আবু ত্বহা মোহাম্মদ আদনান
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: টেনশন করো না, নিশ্চয়ই আল্লাহ সাথে আছেন",
        "url": "https://www.youtube.com/shorts/CYhJPNiBvXA",
        "src_id": "yt_CYhJPNiBvXA",
        "nasihat": "বিপদাপদে আল্লাহর ওপর পূর্ণ তাওয়াক্কুল রাখুন, নিশ্চয়ই তিনি ধৈর্যশীলদের সাহায্য করেন।",
        "hashtags": "#AbuTohaAdnan #AbuTohaWaz #Tawakkul #PeaceOfMind"
    },
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: অন্তরের অন্তস্থল থেকে রবের কাছে চান",
        "url": "https://www.youtube.com/shorts/3i_n006zR5c",
        "src_id": "yt_3i_n006zR5c",
        "nasihat": "মানুষের কাছে হাত না পেতে রবের কাছে চান, তিনি কখনোই বান্দাকে খালি হাতে ফেরান না।",
        "hashtags": "#AbuTohaAdnan #Dua #Faith #Sunnah"
    },
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: শেষ জামানার ঈমান রক্ষার পথ",
        "url": "https://www.youtube.com/shorts/Xo_M1YgHn6s",
        "src_id": "yt_Xo_M1YgHn6s",
        "nasihat": "ফিতনার যুগে নিজের ঈমান ও আমলকে মজবুত রাখুন, কুরআনের ছায়াতলে ফিরে আসুন।",
        "hashtags": "#AbuTohaAdnan #Eman #IslamicReminder #Ummah"
    },

    # ৩. আল্লামা দেলাওয়ার হোসাইন সাঈদী
    {
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "title": "আল্লামা দেলাওয়ার হোসাইন সাঈদী: কুরআনের বাণীই মানুষের মুক্তির একমাত্র পথ",
        "url": "https://www.youtube.com/shorts/Zp0-7uE2R5U",
        "src_id": "yt_Zp0-7uE2R5U",
        "nasihat": "কুরআন কেবল পড়ার কিতাব নয়, কুরআন মানবজাতির জীবন পরিচালনার পরিপূর্ণ বিধান।",
        "hashtags": "#AllamaSayedi #SayediWaz #QuranerDawat #HeartTouchingWaz"
    },
    {
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "title": "আল্লামা দেলাওয়ার হোসাইন সাঈদী: মোমেনের আসল পরিচয় ও আল্লাহর ভয়",
        "url": "https://www.youtube.com/shorts/r7_yN_6gMps",
        "src_id": "yt_r7_yN_6gMps",
        "nasihat": "যার অন্তরে আল্লাহর ভয় আছে, সে কখনো কোনো পাপ কাজে লিপ্ত হতে পারে না।",
        "hashtags": "#AllamaSayedi #SayediBayan #Taqwa #Eman"
    },

    # ৪. শায়খ আহমাদুল্লাহ
    {
        "scholar": "শায়খ আহমাদুল্লাহ",
        "title": "শায়খ আহমাদুল্লাহ: অন্তরের সংকীর্ণতা দূর করার উপায় ও প্রশান্তি",
        "url": "https://www.youtube.com/shorts/Jk_8_4sXw6U",
        "src_id": "yt_Jk_8_4sXw6U",
        "nasihat": "মানুষের ওপর রাগ ও ক্ষোভ পুষে রাখবেন না। ক্ষমা করে দিন, আল্লাহ আপনাকে ক্ষমা করবেন।",
        "hashtags": "#ShaykhAhmadullah #AhmadullahWaz #HeartPeace #LifeHacks"
    },

    # ৫. মাওলানা তারেক জামিল
    {
        "scholar": "মাওলানা তারেক জামিল",
        "title": "মাওলানা তারেক জামিল: অন্তরের প্রশান্তি ও আল্লাহর অসীম রহমত",
        "url": "https://www.youtube.com/shorts/B8m_Lp7wY6o",
        "src_id": "yt_B8m_Lp7wY6o",
        "nasihat": "আল্লাহ কাউকে শাস্তি দিতে চান না, তিনি চান বান্দা তওবা করে ফিরে আসুক।",
        "hashtags": "#MaulanaTariqJamil #TariqJamilBangla #Tawbah #AllahMercy"
    }
]

# ডায়নামিক সার্চ কুয়েরি
DYNAMIC_SCHOLAR_QUERIES = [
    ("মাওলানা মিজানুর রহমান আজহারী", "মিজানুর রহমান আজহারী shorts #shorts", "#MizanurRahmanAzhari #AzhariWaz"),
    ("আবু ত্বহা মোহাম্মদ আদনান", "আবু ত্বহা আদনান shorts #shorts", "#AbuTohaAdnan #AbuTohaWaz"),
    ("আল্লামা দেলাওয়ার হোসাইন সাঈদী", "আল্লামা সাঈদী shorts #shorts", "#AllamaSayedi #SayediWaz"),
    ("শায়খ আহমাদুল্লাহ", "শায়খ আহমাদুল্লাহ shorts #shorts", "#ShaykhAhmadullah #AhmadullahWaz"),
    ("মাওলানা মিজানুর রহমান আজহারী", "আজহারী মোটিভেশনাল shorts #shorts", "#MizanurRahmanAzhari #AzhariShorts"),
    ("মুফতি আমির হামজা", "আমির হামজা shorts #shorts", "#AmirHamzaWaz #AmirHamzaShorts"),
    ("আবু ত্বহা মোহাম্মদ আদনান", "আবু ত্বহা মোহাম্মদ আদনান shorts #shorts", "#AbuTohaAdnan #Eman"),
    ("আল্লামা দেলাওয়ার হোসাইন সাঈদী", "দেলাওয়ার হোসাইন সাঈদী ওয়াজ shorts #shorts", "#AllamaSayedi #SayediShorts"),
    ("মাওলানা তারেক জামিল", "মাওলানা তারেক জামিল বাংলা shorts #shorts", "#MaulanaTariqJamil #TariqJamilBangla"),
    ("মাওলানা মিজানুর রহমান আজহারী", "mizanur rahman azhari waz shorts", "#MizanurRahmanAzhari #ViralWaz")
]

def get_posted_signatures_from_facebook(page_id: str, access_token: str, limit: int = 100) -> set:
    """ফেসবুক পেজ থেকে ইতিমধ্যে পোস্ট হওয়া ভিডিওগুলোর শিরোনাম ও আইডি রিড করে"""
    signatures = set()
    if not access_token or not page_id:
        return signatures
    try:
        url = f"https://graph.facebook.com/v21.0/{page_id}/videos"
        res = requests.get(url, params={"access_token": access_token, "fields": "description,title", "limit": limit}, timeout=15)
        if res.status_code == 200:
            data = res.json().get("data", [])
            for item in data:
                text = (item.get("description", "") + " " + item.get("title", "")).lower()
                m = re.findall(r"\[src:([a-zA-Z0-9_-]+)\]", text)
                for src in m:
                    signatures.add(src)
                for banned in PERMANENT_BANNED_SIGNATURES:
                    if banned.lower() in text:
                        signatures.add(banned)
            logging.info(f"Loaded {len(signatures)} posted signatures from Facebook Graph API.")
    except Exception as e:
        logging.warning(f"Failed to fetch Facebook video signatures: {e}")
    return signatures

def load_local_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"posted_ids": [], "last_scholar_index": -1, "daily_stats": {}}

def save_local_history(history: dict):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.warning(f"Failed to save local history: {e}")

def download_youtube_short(item: dict) -> str:
    """Downloads YouTube Short using android_embedded client to bypass bot checks."""
    src_id = item["src_id"]
    output_path = os.path.join(DOWNLOAD_DIR, f"{src_id}.mp4")

    if os.path.exists(output_path) and os.path.getsize(output_path) > 50000:
        return output_path

    logging.info(f"Downloading authentic YouTube Short: {item['title']} ({item['url']})")
    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android_embedded,web_embedded",
        "--merge-output-format", "mp4",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "-o", output_path,
        "--no-playlist",
        "--socket-timeout", "35",
        "--retries", "3",
        item["url"]
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 50000:
        logging.info(f"Successfully downloaded YouTube Short: {output_path} ({os.path.getsize(output_path)/(1024*1024):.2f} MB)")
        return output_path
    else:
        logging.warning(f"yt-dlp failed for {item['url']}: {res.stderr[:300]}")
        return None

def search_dynamic_youtube_short(scholar_name: str, query: str, default_hashtags: str, posted_signatures: set) -> dict:
    logging.info(f"Searching fresh trending YouTube Shorts for scholar: {scholar_name} ({query})")
    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android_embedded,web_embedded",
        "--flat-playlist",
        "--match-filter", "duration <= 90",
        "--print", "%(id)s|||%(title)s|||%(duration)s",
        f"ytsearch10:{query}"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        lines = [l.strip() for l in res.stdout.strip().split("\n") if l.strip() and "|||" in l]
        for line in lines:
            parts = line.split("|||")
            vid_id = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else query
            src_id = f"yt_{vid_id}"

            if src_id in posted_signatures or any(b in title.lower() for b in PERMANENT_BANNED_SIGNATURES):
                continue

            return {
                "scholar": scholar_name,
                "title": f"{scholar_name}: {title[:70]}",
                "url": f"https://www.youtube.com/shorts/{vid_id}",
                "src_id": src_id,
                "nasihat": "আল্লাহর আনুগত্য ও রাসুলুল্লাহ (সাঃ)-এর সুন্নাহ অনুসরণের মাধ্যমেই অন্তরের প্রকৃত শান্তি ও মুক্তি মেলে।",
                "hashtags": f"{default_hashtags} #Shorts #WazReels"
            }
    except Exception as e:
        logging.warning(f"Dynamic search error for {scholar_name}: {e}")

    return None
