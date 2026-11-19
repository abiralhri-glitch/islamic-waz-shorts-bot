"""
Islamic Waz Short Reels Downloader & YouTube/TikTok Multi-Source Engine
- ১০০% আসল হুজুরদের লাইভ মাহফিল ও নসিহতের আসল সিনেমাটিক শর্ট ভিডিও
- সকল শীর্ষস্থানীয় সম্মানিত ইসলামিক স্কলারগণের অন্তর্ভুক্তিকরণ (আহমাদুল্লাহ, আজহারী, আবু ত্বহা, সাঈদী, আমির হামজা, তারেক জামিল, আব্দুল্লাহ জাহাঙ্গীর, হাফিজুর রহমান সিদ্দিকী প্রমুখ)
- কঠোর জিরো-ডুপ্লিকেট পলিসি: ফেসবুক পেজের পূর্ববর্তী ১০০টি ভিডিওর মেটাডাটা ও হিস্টোরি যাচাই
- ১০০% স্বাভাবিক কণ্ঠস্বর: কোনো কার্টুন পিচ-শিফটিং বা ভয়েস স্পিড ডিস্টরশন নয়
- পেজের স্থায়ী ব্র্যান্ডেড ওয়াটারমার্ক: 'সেরা ইসলামিক শর্ট ওয়াজ'
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

# অপরিবর্তনযোগ্য স্থায়ী ব্ল্যাকলিস্ট (পেজ থেকে ডিলিট করলেও কখনো পুনরায় আপলোড হবে না)
PERMANENT_BANNED_SIGNATURES = {
    "bank_ahmadullah_life_advice",
    "bank_ahmadullah_dua",
    "ahmadullah_life_advice.mp4",
    "ahmadullah_dua.mp4",
    "yt_yXH8rPQ3l2M",
    "yt_y31MzRdIDPo",
    "জীনরা খাবার কোথায় পায়",
    "দোয়ার ফজিলত ও রবকে ডাকার গোপন রহস্য",
    "উত্তম চরিত্র ও সুন্দর পারিবারিক জীবনের শিক্ষা"
}

DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# সকল শীর্ষ সম্মানিত হুজুরদের ভেরিফাইড ট্রেন্ডিং ইউটিউব শর্টস কালেকশন (আজহারী, আবু ত্বহা ও সাঈদী অগ্রাধিকার)
CURATED_YOUTUBE_SHORTS = [
    # ১. মাওলানা মিজানুর রহমান আজহারী (সর্বাধিক প্রাধান্য)
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

    # ২. আবু ত্বহা মোহাম্মদ আদনান (সর্বাধিক প্রাধান্য)
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
        "title": "আবু ত্বহা মোহাম্মদ আদনান: আখিরাতের প্রস্তুতি ও শেষ জামানায় ঈমান রক্ষা",
        "url": "https://www.youtube.com/shorts/_ZT4fMcU17g",
        "src_id": "yt__ZT4fMcU17g",
        "nasihat": "সকাল ও সন্ধ্যার মাসনুন দোয়া এবং সূরা আল-কাহাফ নিয়মিত তিলাওয়াত করুন।",
        "hashtags": "#AbuTohaAdnan #SheshJamana #Eman #IslamicReels"
    },
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: অন্তরের ভয় দূর করার উপায় ও তাওযাক্কুল",
        "url": "https://www.youtube.com/shorts/FMwP2Nq78Jg",
        "src_id": "yt_FMwP2Nq78Jg",
        "nasihat": "বান্দা যখন আল্লাহর ওপর তাওয়াক্কুল করে, আল্লাহ তার জন্য যথেষ্ট হয়ে যান।",
        "hashtags": "#AbuTohaAdnan #Tawakkul #Eman #IslamicReminder"
    },

    # ৩. আল্লামা দেলাওয়ার হোসাইন সাঈদী (সর্বাধিক প্রাধান্য)
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
        "title": "আল্লামা দেলাওয়ার হোসাইন সাঈদী: কালজয়ী আবেগঘন শ্রেষ্ঠ নসিহত ও তওবার আহ্বান",
        "url": "https://www.youtube.com/shorts/u92CrHYHka4",
        "src_id": "yt_u92CrHYHka4",
        "nasihat": "নিশ্চয়ই মহান আল্লাহ তওবাকারীদের অত্যন্ত ভালোবাসেন। বিলম্ব না করে ফিরে আসুন।",
        "hashtags": "#AllamaSayedi #SayediShorts #HeartTouching #Tawbah"
    },

    # ৪. শায়খ আহমাদুল্লাহ (ভাইরাল বক্তা)
    {
        "scholar": "শায়খ আহমাদুল্লাহ",
        "title": "শায়খ আহমাদুল্লাহ: প্রতিদিন করার মত ছোট ছোট কিছু আমল ও ফজিলত",
        "url": "https://www.youtube.com/shorts/454Qn82o4FY",
        "src_id": "yt_454Qn82o4FY",
        "nasihat": "দৈনন্দিন ছোট ছোট নেক আমলই আখিরাতে আপনার মিজান ভারী করে দিবে। নিয়মিত আমল করুন।",
        "hashtags": "#ShaykhAhmadullah #AhmadullahWaz #IslamicReminder #Sunnah #DailyAmol"
    },

    # ৫. মুফতি আমির হামজা (ভাইরাল বক্তা)
    {
        "scholar": "মুফতি আমির হামজা",
        "title": "মুফতি আমির হামজা: জীবনের শ্রেষ্ঠ বাস্তবতা ও পারিবারিক সৌহার্দ্য",
        "url": "https://www.youtube.com/shorts/bs5QoImTpA4",
        "src_id": "yt_bs5QoImTpA4",
        "nasihat": "পরিবারের প্রতি সদয় হোন এবং রাসুলুল্লাহ (সা.)-এর সুন্নাহ মোতাবেক জীবন পরিচালনা করুন।",
        "hashtags": "#AmirHamza #AmirHamzaWaz #BanglaWaz #Sunnah"
    },

    # ৬. মাওলানা তারেক জামিল (ভাইরাল বক্তা)
    {
        "scholar": "মাওলানা তারেক জামিল",
        "title": "মাওলানা তারেক জামিল: অন্তরের নীরব কান্না ও মহান রবের ক্ষমা",
        "url": "https://www.youtube.com/shorts/Pjl_pOe18vA",
        "src_id": "yt_Pjl_pOe18vA",
        "nasihat": "মহান আল্লাহ তার বান্দার প্রতিটি অশ্রুবিন্দু দেখেন। একান্তে আল্লাহর কাছে ক্ষমা চান।",
        "hashtags": "#MaulanaTariqJamil #TariqJamilBangla #HeartTouchingWaz #Peace"
    },
    {
        "scholar": "মাওলানা তারেক জামিল",
        "title": "মাওলানা তারেক জামিল: দুনিয়ার ক্ষণস্থায়িত্ব ও আখিরাতের অনন্ত জীবন",
        "url": "https://www.youtube.com/shorts/_PK-8d2tSQ0",
        "src_id": "yt__PK-8d2tSQ0",
        "nasihat": "দুনিয়া হচ্ছে মুসাফিরের মতো ছায়ার জায়গা, আসল গন্তব্য আখিরাত। আখেরাতমুখী হোন।",
        "hashtags": "#TariqJamil #TariqJamilEmotional #IslamicReminder"
    }
]

# ডায়নামিক সার্চ কুয়েরি (আজহারী, আবু ত্বহা ও সাঈদী সর্বাধিক প্রাধান্য রোটেশন)
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
                # শিরোনামের কীওয়ার্ড চেক
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
    src_id = item["src_id"]
    output_path = os.path.join(DOWNLOAD_DIR, f"{src_id}.mp4")

    if os.path.exists(output_path) and os.path.getsize(output_path) > 50000:
        return output_path

    logging.info(f"Downloading authentic YouTube Short: {item['title']} ({item['url']})")
    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android",
        "-f", "best/b/18",
        "-o", output_path,
        "--no-playlist",
        "--socket-timeout", "30",
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
        "--extractor-args", "youtube:player_client=android",
        "--flat-playlist",
        "--match-filter", "duration <= 90",
        "--print", "%(id)s|||%(title)s|||%(duration)s",
        f"ytsearch10:{query}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        return None

    for line in res.stdout.strip().splitlines():
        parts = line.split("|||")
        if len(parts) >= 2:
            vid_id = parts[0].strip()
            title = parts[1].strip()
            src_id = f"yt_{vid_id}"

            if src_id in posted_signatures or vid_id in posted_signatures:
                continue
            is_banned = False
            for b in PERMANENT_BANNED_SIGNATURES:
                if b.lower() in title.lower() or b == src_id:
                    is_banned = True
                    break
            if is_banned:
                continue

            return {
                "scholar": scholar_name,
                "title": f"{scholar_name}: {title}",
                "url": f"https://www.youtube.com/shorts/{vid_id}",
                "src_id": src_id,
                "nasihat": "দ্বীনের সহিহ বার্তা জানুন এবং জীবনঘনিষ্ঠ আমলের মাধ্যমে পরকালকে সুন্দর করুন।",
                "hashtags": f"{default_hashtags} #IslamicShorts #BanglaWaz #Sunnah #Eman"
            }
    return None
